# BLE scanner based on https://github.com/adamf/BLE/blob/master/ble-scanner.py
# BLE scanner, based on https://code.google.com/p/pybluez/source/browse/trunk/examples/advanced/inquiry-with-rssi.py

# https://github.com/pauloborges/bluez/blob/master/tools/hcitool.c for lescan
# https://kernel.googlesource.com/pub/scm/bluetooth/bluez/+/5.6/lib/hci.h for opcodes
# https://github.com/pauloborges/bluez/blob/master/lib/hci.c#L2782 for functions used by lescan

# NOTE: Python's struct.pack() will add padding bytes unless you make the endianness explicit. Little endian
# should be used for BLE. Always start a struct.pack() format string with "<"
import sys, struct, logging, Queue
import bluetooth._bluetooth as bluez
import time

LE_META_EVENT = 0x3e
LE_PUBLIC_ADDRESS = 0x00
LE_RANDOM_ADDRESS = 0x01
LE_SET_SCAN_PARAMETERS_CP_SIZE = 7
OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_PARAMETERS = 0x000B
OCF_LE_SET_SCAN_ENABLE = 0x000C
OCF_LE_CREATE_CONN = 0x000D

LE_ROLE_MASTER = 0x00
LE_ROLE_SLAVE = 0x01

# these are actually subevents of LE_META_EVENT
EVT_LE_CONN_COMPLETE = 0x01
EVT_LE_ADVERTISING_REPORT = 0x02
EVT_LE_CONN_UPDATE_COMPLETE = 0x03
EVT_LE_READ_REMOTE_USED_FEATURES_COMPLETE = 0x04

# Advertisment event types
ADV_IND = 0x00
ADV_DIRECT_IND = 0x01
ADV_SCAN_IND = 0x02
ADV_NONCONN_IND = 0x03
ADV_SCAN_RSP = 0x04

logger = logging.getLogger(__name__)
is_running = True
server_time_offset = 0
adv_scan_rsp = {}


def return_number_from_packet(pkt):
    myInteger = 0
    multiple = 256
    for c in pkt:
        myInteger += struct.unpack('B', c)[0] * multiple
        multiple = 1
    return myInteger


def return_string_from_packet(pkt):
    myString = ''
    for c in pkt:
        myString += '%02x' % struct.unpack('B', c)[0]
    return myString


def print_packet(pkt):
    for c in pkt:
        sys.stdout.write('%02x ' % struct.unpack('B', c)[0])


def get_packed_bdaddr(bdaddr_string):
    packable_addr = []
    addr = bdaddr_string.split(':')
    addr.reverse()
    for b in addr:
        packable_addr.append(int(b, 16))
    return struct.pack('<BBBBBB', *packable_addr)


def packed_bdaddr_to_string(bdaddr_packed):
    return ':'.join('%02x' % i for i in struct.unpack('BBBBBB', bdaddr_packed[::-1]))


def hci_enable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x01)


def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)


def hci_toggle_le_scan(sock, enable):
    cmd_pkt = struct.pack('<BB', enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)
    logger.info('Toggled le scan: %s', enable)


def hci_le_set_scan_parameters(sock):
    SCAN_RANDOM = 0x01
    OWN_TYPE = SCAN_RANDOM
    SCAN_TYPE = 0x01
    WINDOW = 0x10
    INTERVAL = 0x10
    FILTER = 0x00  # all advertisements, not just whitelisted devices

    # interval and window are uint_16, so we pad them with 0x0
    cmd_pkt = struct.pack('<BBBBBBB', SCAN_TYPE, 0x0, INTERVAL, 0x0, WINDOW, OWN_TYPE, FILTER)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_PARAMETERS, cmd_pkt)
    logger.info('Sent scan parameters command.')


def parse_events(sock, queue, loop_count=100):
    logger.info('Started parsing BLE events...')
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # perform a device inquiry on bluetooth device #0
    # The inquiry should last 8 * 1.28 = 10.24 seconds
    # before the inquiry is performed, bluez should flush its cache of
    # previously discovered devices
    filter = bluez.hci_filter_new()
    bluez.hci_filter_all_events(filter)
    bluez.hci_filter_set_ptype(filter, bluez.HCI_EVENT_PKT)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, filter)

    for i in range(0, loop_count):
        if not is_running:
            break

        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack('BBB', pkt[:3])

        if event == LE_META_EVENT:
            subevent, = struct.unpack('B', pkt[3])
            pkt = pkt[4:]
            if subevent == EVT_LE_ADVERTISING_REPORT:
                num_reports = struct.unpack('B', pkt[0])[0]
                report_offset = 0
                for i in range(0, num_reports):
                    # print 'Raw: ', return_string_from_packet(pkt)
                    report_event_type = struct.unpack("B", pkt[report_offset + 1])[0]
                    mac = packed_bdaddr_to_string(pkt[report_offset + 3: report_offset + 9])

                    report_data_length = struct.unpack("B", pkt[report_offset + 9])[0]

                    pkt = pkt[report_offset + 10:]

                    if report_event_type == ADV_IND:
                        # print "\tADV_IND"
                        adv_scan_rsp[mac] = pkt[:report_data_length]
                        continue
                    elif report_event_type == ADV_DIRECT_IND:
                        # print "\tADV_DIRECT_IND"
                        adv_scan_rsp[mac] = pkt[:report_data_length]
                        continue
                    elif report_event_type == ADV_SCAN_IND:
                        # print "\tADV_SCAN_IND"
                        adv_scan_rsp[mac] = pkt[:report_data_length]
                        continue
                    # elif report_event_type == ADV_NONCONN_IND:
                        # print "\tADV_NONCONN_IND"
                    elif report_event_type == ADV_SCAN_RSP:
                        # print "\tADV_SCAN_RSP"
                        previous_pkt = adv_scan_rsp.get(mac, None)
                        if previous_pkt is not None:
                            del adv_scan_rsp[mac]
                            pkt = previous_pkt + pkt[report_offset:]
                    # else:
                        # print "\tUnknown or reserved event type"

                    try:
                        manufacturer = return_string_from_packet(pkt[report_offset + 5: 7])
                        if manufacturer.lower() == 'c6a0':  # Ignore mac address if Gimbal
                            mac = ''

                        ble_type = return_string_from_packet(pkt[report_offset + 7: 9])

                        # Get UUID
                        if report_data_length > report_offset + 25 and \
                            manufacturer.lower() == '4c00' and ble_type.lower() == '0215':
                            uuid = return_string_from_packet(pkt[report_offset + 9: report_offset + 25])
                        elif report_data_length > report_offset + 31 and \
                            manufacturer.lower() == 'c6a0':
                            uuid = return_string_from_packet(pkt[report_offset + 22: report_offset + 31])
                        else:
                            uuid = ''

                        # Get Data
                        if uuid == '' and report_data_length > report_offset + 9:
                            data = return_string_from_packet(pkt[report_offset + 9: -1])
                        elif report_data_length > report_offset + 25 and \
                            manufacturer.lower() != 'c6a0':
                            data = return_string_from_packet(pkt[report_offset + 25: -1])
                        else:
                            data = ''

                        # major = return_number_from_packet(pkt[report_offset + 25: report_offset + 27])
                        # minor = return_number_from_packet(pkt[report_offset + 27: report_offset + 29])
                        # power = struct.unpack('b', pkt[report_offset + 29])[0]
                        if report_data_length > report_offset + 30:
                            battery = struct.unpack('b', pkt[report_offset + 30])[0]
                        else:
                            battery = 0

                        rssi = struct.unpack('b', pkt[-1])[0]

                        now = int(time.time() * 1000) + server_time_offset
                        previous_item = queue.queue[-1] if not queue.empty() else {}  # dict()
                        if uuid != previous_item.get('beacon_uid', None) or \
                                (uuid == previous_item.get('beacon_uid', None) and
                                         (now - previous_item.get('timestamp')) >= 1000):
                            logger.debug('Raw: %s', return_string_from_packet(pkt))
                            logger.info('Parsed: %s,%s,%s,%s,%i,%i' % (mac, manufacturer, uuid, data, battery, rssi))
                            print 'Parsed: %s,%s,%s,%s,%i,%i' % (mac, manufacturer, uuid, data, battery, rssi)

                            sighting = {}  # dict()
                            sighting['timestamp'] = now
                            sighting['beacon_mac'] = mac.replace(':', '')
                            sighting['beacon_uid'] = uuid
                            sighting['beacon_battery'] = battery
                            sighting['rssi'] = rssi
                            queue.put(sighting)
                        # else:
                            # logger.info('Skipping packet as a similar one happened less than 1 second ago.')

                    except Exception as ex:
                        logger.exception('Failed to parse beacon advertisement package:')

                    report_offset = report_offset +  10 + report_data_length + 1


    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)
    logger.info('Finished parsing events.')
