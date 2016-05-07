#!/usr/bin/env python
from datetime import datetime
import os, sys, subprocess, logging
import time, requests, json, urllib, zipfile
import config, blescan

logger = logging.getLogger(__name__)

def respawn_script(ble_thread=None):
    if ble_thread is not None:
        logger.info('Daily or on update re-spawn, stopping BLE thread...')
        blescan.is_running = False
        ble_thread.join()
        logger.info('BLE thread stopped.')

    logger.info('Restarting script...')
    config.set('DEVICE', 'last_respawn_date', datetime.now().strftime("%Y-%m-%d"))
    config.save()

    subprocess.call([config.HCICONFIG_FILE_PATH, 'hci0', 'down'])
    os.execv(config.BASE_APP_PATH + 'ivigilate.py', sys.argv)


def restart_pi():
    logger.info('Sending restart command to Raspberry Pi...')
    config.save()

    command = "/usr/bin/sudo /sbin/shutdown -r now"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output


def check(ble_thread=None):
    metadata = json.dumps({'hardware': config.get('DEVICE', 'hardware'),
                           'revision': config.get('DEVICE', 'revision'),
                           'os_uname': config.get('DEVICE', 'uname'),
                           'last_update_date': config.get('DEVICE', 'last_update_date')})
    data = json.dumps({'company_id': config.get('BASE', 'company_id'),
                       'detector_uid': config.get('DEVICE', 'hardware') + config.get('DEVICE', 'revision') + config.get('DEVICE', 'serial'),
                       'metadata': metadata})

    response = None
    iteration = 0
    while response == None:
        try:
            response = requests.post(config.get('SERVER', 'address') + config.get('SERVER', 'autoupdate_uri'),
                                     data, verify=True)
            logger.debug('check() received from server: %s', response)
        except Exception:
            logger.exception('check() failed to contact the server with error:')
            if iteration < 3:
                time.sleep(5)
                iteration = iteration + 1
            else:
                restart_pi()

    if response.status_code == 200:  # Everything is up-to-date
        logger.info('check() returned 200 OK (Everything is up-to-date).')
        return
    elif response.status_code == 412:
        now = datetime.now()
        update = json.loads(response.text)

        if 'config' in update:
            try:
                for cfg in update['config']:
                    logger.debug('check() is updating the following config setting: %s', cfg)
                    config.set(cfg[0], cfg[1], cfg[2])
            except Exception:
                logger.exception('check() failed to update configuration with error:')
                return

        if 'files' in update:
            try:
                for file in update['files']:
                    logger.info('check() is retrieving the following file: \'%s\'', file)
                    urllib.urlretrieve(file['src'], file['dst'])
                    if zipfile.is_zipfile(file['dst']):
                        logger.info('check() is unzipping the following file: \'%s\'', file['dst'])
                        zipfile.ZipFile(file['dst']).extractall(config.BASE_APP_PATH)

            except Exception:
                logger.exception('check() failed to update file with exception:')
                return

        config.set('DEVICE', 'last_update_date', now.strftime("%Y-%m-%d %H:%M"))
        if update['restart']:
            restart_pi()
        else:
            respawn_script(ble_thread)
        sys.exit()
    else:
        logger.warn('check() returned %s. Ignoring and continuing work...', response.status_code)
        return