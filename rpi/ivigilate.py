#!/usr/bin/env python
from datetime import datetime, timedelta
import os, sys, subprocess, ConfigParser, logging
import time, requests, json, Queue, threading
import config, autoupdate, blescan
import bluetooth._bluetooth as bluez
import buzzer
from logging.handlers import RotatingFileHandler

__logger = logging.getLogger(__name__)

__dev_id = 0

__ignore_sightings_lock = threading.Lock()
__ignore_sightings = {}

__invalid_detector_check_timestamp = 0

IGNORE_INTERVAL = 60 * 60 * 1000


def init_logger(log_level):
    log_formatter = logging.Formatter('%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s')

    file_handler = RotatingFileHandler(config.LOG_FILE_PATH, mode='a', maxBytes=2*1024*1024,
                                     backupCount=10, encoding=None, delay=0)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(log_level)

    __logger.addHandler(file_handler)


def send_sightings_async(sightings):
    t = threading.Thread(target=send_sightings, args=(sightings,))
    t.start()


def send_sightings(sightings):
    global __invalid_detector_check_timestamp

    for sighting in sightings:
        sighting['detector_uid'] = config.get_detector_uid()
        sighting['detector_battery'] = None  # this can be used in the future...

    try:
        __logger.info('Sending %s sightings to the server...', len(sightings))
        response = requests.post(config.get('SERVER', 'address') + config.get('SERVER', 'addsightings_uri'),
                                 json.dumps(sightings), verify=True)
        __logger.info('Received from addsightings: %s - %s', response.status_code, response.text)

        result = json.loads(response.text)
        now = int(time.time() * 1000)
        blescan.server_time_offset = result.get('timestamp', now) - now
        __invalid_detector_check_timestamp = 0

        if response.status_code >= 400 and response.status_code < 500:
            __invalid_detector_check_timestamp = now + blescan.server_time_offset
            __logger.warning('Detector is marked as invalid. Ignoring ALL sightings for %i ms', IGNORE_INTERVAL)
        elif response.status_code == 206:
            if result.get('data', None) is not None and len(result.get('data')) > 0:
                __ignore_sightings_lock.acquire()

                for ignore_sighting_key in result.get('data'):
                    __ignore_sightings[ignore_sighting_key] = now + blescan.server_time_offset

                __ignore_sightings_lock.release()

    except Exception:
        __logger.exception('Failed to contact the server with error:')

def init_ble_advertiser():
    # Configure Ble advertisement packet
    ble_adv_string = '1e02011a1aff4c000215' + config.get_detector_uid() + '00000000c500000000000000000000000000'
    ble_adv_array = [ble_adv_string[i:i+2] for i in range(0,len(ble_adv_string),2)]

    hci_tool_params = [config.HCITOOL_FILE_PATH, '-i', 'hci0', 'cmd', '0x08', '0x0008']
    hci_tool_params.extend(ble_adv_array)
    subprocess.call(hci_tool_params)

    # Configure Ble advertisement rate
    # (check http://stackoverflow.com/questions/21124993/is-there-a-way-to-increase-ble-advertisement-frequency-in-bluez for math)
    ble_config_string = '000800080300000000000000000700'
    ble_config_array = [ble_config_string[i:i+2] for i in range(0,len(ble_config_string),2)]

    hci_tool_params = [config.HCITOOL_FILE_PATH, '-i', 'hci0', 'cmd', '0x08', '0x0006']
    hci_tool_params.extend(ble_config_array)
    subprocess.call(hci_tool_params)

    # Start Ble advertisement
    subprocess.call([config.HCITOOL_FILE_PATH, '-i', 'hci0', 'cmd', '0x08', '0x000a', '01'])

def ble_scanner(queue):
    try:
        sock = bluez.hci_open_dev(__dev_id)
        __logger.info('BLE device started')
    except Exception:
        __logger.exception('BLE device failed to start:')

        __logger.critical('Will reboot RPi to see if it fixes the issue')
        # try to stop and start the BLE device somehow...
        # if that doesn't work, reboot the device.
        __logger.critical('Will reboot RPi to see if it fixes the issue')
        sys.exit(1)

    blescan.hci_le_set_scan_parameters(sock)
    blescan.hci_enable_le_scan(sock)

    while blescan.is_running:
        blescan.parse_events(sock, queue, 50)  # every 50 events 'refresh' the ble socket...whatever that means


def main():
    locally_seen_macs = set() # Set that contains unique locally seen beacons
    locally_seen_uids = set() # Set that contains unique locally seen beacons
    authorized = set()
    authorized.add('b0b448fba565')
    authorized.add('123456781234123412341234567890ab')
    unauthorized = set(['b0b448c87401'])
    
    config.init()
    buzzer.init()

    log_level = config.getint('BASE', 'log_level')
    init_logger(log_level)

    __logger.info('Started with log level: ' + logging.getLevelName(log_level))

    #autoupdate.check()
    last_update_check = datetime.now()

    # need to try catch and retry this as it some times fails...
    subprocess.call([config.HCICONFIG_FILE_PATH, 'hci0', 'up'])

    init_ble_advertiser()

    ble_queue = Queue.Queue()

    ble_thread = threading.Thread(target=ble_scanner, args=(ble_queue,))
    ble_thread.daemon = True
    ble_thread.start()
    __logger.info('BLE scanner thread started')

    last_respawn_date = datetime.strptime(config.get('DEVICE', 'last_respawn_date'), '%Y-%m-%d').date()
    
    print "Going into the main loop..."
    print "Authorized: ", authorized
    print "Unauthorized: ", unauthorized 

    try:
        while True:
            now = datetime.now()
            now_timestamp = int(time.time() * 1000)
            # if configured daily_respawn_hour, stop the ble_thread and respawn the process
            # if now.date() > last_respawn_date and now.hour == config.getint('BASE', 'daily_respawn_hour'):
                # autoupdate.respawn_script(ble_thread)
                # autoupdate.restart_pi()
            # elif now > last_update_check + timedelta(minutes=5):
                # autoupdate.check(ble_thread)
                # last_update_check = datetime.now()

            # Take new sightings from queue
            sightings = []
            for i in range(100):
                if ble_queue.empty():
                    break
                else:
                    sighting = ble_queue.get()
                    sighting_key = sighting['beacon_mac'] + sighting['beacon_uid']

                    ignore_sighting = now_timestamp - __invalid_detector_check_timestamp < IGNORE_INTERVAL
                    if not ignore_sighting:
                        __ignore_sightings_lock.acquire()

                        ignore_sighting_timestamp = __ignore_sightings.get(sighting_key, 0)
                        if ignore_sighting_timestamp > 0 and \
                            now_timestamp - ignore_sighting_timestamp < IGNORE_INTERVAL:
                            ignore_sighting = True
                        elif sighting_key in __ignore_sightings:
                            del __ignore_sightings[sighting_key]

                        __ignore_sightings_lock.release()

                    if not ignore_sighting:
                        sightings.append(sighting)
                        # TODO Only add this beacon to the list if we have "events" for it
                        ## Probably join all unauthorized lists into one and see if this new exists there or not
                        if sighting['beacon_mac'] != '':
                            locally_seen_macs.add(sighting['beacon_mac']) # Append the beacon_mac of the latest sighting
                        if sighting['beacon_uid'] != '':
                            locally_seen_uids.add(sighting['beacon_uid']) # Append the beacon_uid of the latest sighting
                        # Launch threading.timer here
                    else:
                        print 'sighting ignored: ' + sighting_key
                    
           # print locally_seen

            # Local events handling
            if not locally_seen_macs.isdisjoint(unauthorized) or \
                not locally_seen_uids.isdisjoint(unauthorized):
                # Rogue beacon is trying to escape!!
                # TODO Add delay to checking authorized sightings
                print "oh oh"
                if (len(locally_seen_macs) == 0 or
                        locally_seen_macs.isdisjoint(authorized)) and \
                    (len(locally_seen_uids) == 0 or
                        locally_seen_uids.isdisjoint(authorized)):
                    # no authorized beacon in sigh
                    buzzer.play_alert(3)
                    
                print "All your base are belong to us."
                locally_seen_macs.clear()
                locally_seen_uids.clear()
            # else:
            #    print "What? Nothing to do..."
                
            # if new sightings, send them to the server
            if len(sightings) > 0:
                send_sightings(sightings)

            time.sleep(1)
            
    except Exception:
        buzzer.end() # Ensure we leave everything nice and clean
        __logger.exception('main() loop failed with error:')
        autoupdate.respawn_script(ble_thread)
        

if __name__ == '__main__':
    main()
