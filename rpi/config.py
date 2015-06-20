#!/usr/bin/env python
import os, ConfigParser, logging

BASE_APP_PATH = '/usr/local/bin/ivigilate/'
LOG_FILE_PATH = '/var/log/ivigilate.log'
HCICONFIG_FILE_PATH = '/usr/sbin/hciconfig'

__cfg = None
logger = logging.getLogger(__name__)


def get_cpuinfo():
    hardware = ''
    revision = ''
    cpuserial = '0000000000000000'
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:8] == 'Hardware':
                hardware = line[11:len(line) - 1]
            elif line[0:8] == 'Revision':
                revision = line[11:len(line) - 1]
            if line[0:6] == 'Serial':
                cpuserial = line[10:len(line) - 1]
        f.close()
    except:
        pass

    return (hardware, revision, cpuserial)


def init():
    global __cfg
    __cfg = ConfigParser.SafeConfigParser()
    __cfg.read(BASE_APP_PATH + 'ivigilate.conf')

    cpuinfo = get_cpuinfo()
    __cfg.set('DEVICE', 'hardware', cpuinfo[0])
    __cfg.set('DEVICE', 'revision', cpuinfo[1])
    __cfg.set('DEVICE', 'serial', cpuinfo[2])
    __cfg.set('DEVICE', 'uname', str(os.uname()))

    if not __cfg.has_option('DEVICE', 'last_respawn_date'):
        __cfg.set('DEVICE', 'last_respawn_date', '2000-01-01')
    if not __cfg.has_option('DEVICE', 'last_update_date'):
        __cfg.set('DEVICE', 'last_update_date', '2000-01-01 00:00')


def set(section, var, value):
    return __cfg.set(section, var, value)


def get(section, var):
    return __cfg.get(section, var)


def getint(section, var):
    return __cfg.getint(section, var)


def save():
    with open(CONFIG_FILE_PATH, 'wb') as file:
        __cfg.write(file)

