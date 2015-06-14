#!/usr/bin/env python
from datetime import datetime
import os, sys, subprocess, ConfigParser, logging
import time, requests, json, Queue, threading, urllib
import config, autoupdate, blescan
import bluetooth._bluetooth as bluez

LOG_FILE_PATH = '/var/log/ivigilate.log'
dev_id = 0
logger = logging.getLogger(__name__)


def init_logger(log_level):
    logging.basicConfig(filename=LOG_FILE_PATH, level=log_level,
                        format='%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s')


def send_sighting(beacon_uuid, beacon_rssi, beacon_battery):
    data = json.dumps(
        {'company_id': config.get('BASE', 'company_id'),
         'beacon_uid': beacon_uuid,
         'watcher_uid': config.get('DEVICE', 'hardware') + config.get('DEVICE', 'revision') + config.get('DEVICE', 'serial'),
         'rssi': beacon_rssi,
         'battery': beacon_battery})

    try:
        response = requests.post(config.get('SERVER', 'address') + config.get('SERVER', 'addsighting_uri'),
                                 data)
        logger.debug('Received from addsighting: %s', response)
    except Exception:
        logger.exception('Failed to contact the server with error:')


def ble_scanner(queue):
    try:
        sock = bluez.hci_open_dev(dev_id)
        logger.info('BLE device started')
    except Exception:
        logger.exception('BLE device failed to start:')

        logger.critical('Will reboot RPi to see if it fixes the issue')
        # try to stop and start the BLE device somehow...
        # if that doesn't work, reboot the device.
        logger.critical('Will reboot RPi to see if it fixes the issue')
        sys.exit(1)

    blescan.hci_le_set_scan_parameters(sock)
    blescan.hci_enable_le_scan(sock)

    while blescan.is_running:
        blescan.parse_events(sock, queue, 50)  # every 50 events 'refresh' the ble socket...whatever that means


def main():
    config.init()

    log_level = config.getint('BASE', 'log_level')
    init_logger(log_level)

    logger.info('Started with log level: ' + logging.getLevelName(log_level))

    autoupdate.check()

    subprocess.call(['/usr/sbin/hciconfig', 'hci0', 'up'])

    ble_queue = Queue.Queue()

    ble_thread = threading.Thread(target=ble_scanner, args=(ble_queue,))
    ble_thread.daemon = True
    ble_thread.start()
    logger.info('BLE scanner thread started')

    last_respawn_date = datetime.strptime(config.get('DEVICE', 'last_respawn_date'), "%Y-%m-%d").date()
    while True:
        now = datetime.now()
        # if configured daily_respawn_hour, stop the ble_thread and respawn the process
        if now.date() > last_respawn_date and now.hour == config.getint('BASE', 'daily_respawn_hour'):
            # update configuration with current date
            config.set('DEVICE', 'last_respawn_date', now.strftime("%Y-%m-%d"))
            config.save()
            autoupdate.respawn_script(ble_thread)

        # if new sighting, send it to the server
        if not ble_queue.empty():
            sighting = ble_queue.get()
            send_sighting(sighting[1], sighting[2], sighting[3])

        time.sleep(0.25)


if __name__ == '__main__':
    main()