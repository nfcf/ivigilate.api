#!/usr/bin/env python
import os, ConfigParser, logging

BASE_APP_PATH = '/usr/local/bin/ivigilate/'
LOG_FILE_PATH = '/var/log/ivigilate.log'
HCICONFIG_FILE_PATH = '/usr/sbin/hciconfig'
HCITOOL_FILE_PATH = '/usr/bin/hcitool'

__cfg = None
__cpuinfo = None
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

def get_detector_uid():
    return 'FFFFFFFFFFFF' + get('DEVICE', 'revision') + get('DEVICE', 'serial')

def init():
    global __cfg
    __cfg = ConfigParser.SafeConfigParser()
    __cfg.readfp(open(BASE_APP_PATH + 'defaults.conf'))  # Load defaults
    __cfg.read(BASE_APP_PATH + 'ivigilate.conf')

    global __cpuinfo
    __cpuinfo = get_cpuinfo()


def set(section, var, value):
    return __cfg.set(section, var, value)


def get(section, var):
    if (section == 'DEVICE'):
        if (var == 'hardware'):
            return __cpuinfo[0]
        elif (var == 'revision'):
            return __cpuinfo[1]
        elif (var == 'serial'):
            return __cpuinfo[2]
        elif (var == 'uname'):
            return str(os.uname())

    return __cfg.get(section, var)


def getint(section, var):
    return __cfg.getint(section, var)


def save():
    with open(BASE_APP_PATH + 'ivigilate.conf', 'wb') as file:
        __cfg.write(file)

