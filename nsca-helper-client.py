import os
import sys
import requests
import simplejson
from optparse import OptionParser

import utils

from __exceptions__ import formattedException

'''
Requires:  requests   http://docs.python-requests.org/en/latest/
'''

__version__ = '1.0.0'

import logging
from logging import handlers

__PROGNAME__ = os.path.splitext(os.path.basename(sys.argv[0]))[0]
LOG_FILENAME = os.sep.join([os.path.dirname(sys.argv[0]),'%s.log' % (__PROGNAME__)])

class MyTimedRotatingFileHandler(handlers.TimedRotatingFileHandler):
    def __init__(self, filename, maxBytes=0, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
	handlers.TimedRotatingFileHandler.__init__(self, filename=filename, when=when, interval=interval, backupCount=backupCount, encoding=encoding, delay=delay, utc=utc)
	self.maxBytes = maxBytes
    
    def shouldRollover(self, record):
	response = handlers.TimedRotatingFileHandler.shouldRollover(self, record)
	if (response == 0):
	    if self.stream is None:                 # delay was set...
		self.stream = self._open()
	    if self.maxBytes > 0:                   # are we rolling over?
		msg = "%s\n" % self.format(record)
		try:
		    self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
		    if self.stream.tell() + len(msg) >= self.maxBytes:
			return 1
		except:
		    pass
	    return 0
	return response

logger = logging.getLogger(__PROGNAME__)
handler = logging.FileHandler(LOG_FILENAME)
#handler = handlers.TimedRotatingFileHandler(LOG_FILENAME, when='d', interval=1, backupCount=30, encoding=None, delay=False, utc=False)
#handler = MyTimedRotatingFileHandler(LOG_FILENAME, maxBytes=1000000, when='d', backupCount=30)
#handler = handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1000000, backupCount=30, encoding=None, delay=False)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler) 
print 'Logging to "%s".' % (handler.baseFilename)

ch = logging.StreamHandler()
ch_format = logging.Formatter('%(asctime)s - %(message)s')
ch.setFormatter(ch_format)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

logging.getLogger().setLevel(logging.DEBUG)

__username__ = 'nscahelper'
__password__ = utils.md5('peekab00')

if __name__ == '__main__':
    '''
    python nsca-helper-client.py

	/nsca/nagios/create/config
	{"oper": "login",
	"username": "nscahelper",
	"password": "103136174d231aabe1de8feaf9afc92f",
	"target": "nagios.cfg",
	"cfg": "remote2_nagios2",
	"partitions": "awk '{print $4}' /proc/partitions | sed -e '/name/d' -e '/^$/d' -e '/[1-9]/!d'",
	"host1": {
		"use": "generic-host",
		"host_name": "remote1",
		"alias": "remote1",
		"address": "0.0.0.0"
	},
	"command1": {
		"command_name": "dummy_command2",
		"command_line": "echo \"0\""
	          },
	  "service1": { "use":"generic-service",
	                "host_name":"remote1",
			"service_description":"CPULoad",
			"active_checks_enabled":"0",
			"passive_checks_enabled":"1",
			"check_command":"dummy_command2"
	          },
	  "service2": { "use":"generic-service",
	                "host_name":"remote1",
			"service_description":"CurrentUsers",
			"active_checks_enabled":"0",
			"passive_checks_enabled":"1",
			"check_command":"dummy_command2"
	          },
	  "service3": { "use":"generic-service",
	                "host_name":"remote1",
			"service_description":"PING",
			"active_checks_enabled":"0",
			"passive_checks_enabled":"1",
			"check_command":"dummy_command2"
	          },
	  "service4": { "use":"generic-service",
	                "host_name":"remote1",
			"service_description":"SSH",
			"active_checks_enabled":"0",
			"passive_checks_enabled":"1",
			"check_command":"dummy_command2"
	          },
	  "service5": { "use":"generic-service",
	                "host_name":"remote1",
			"service_description":"TotalProcesses",
			"active_checks_enabled":"0",
			"passive_checks_enabled":"1",
			"check_command":"dummy_command2"
	          },
	  "service6": { "use":"generic-service",
	                "host_name":"remote1",
			"service_description":"ZombieProcesses",
			"active_checks_enabled":"0",
			"passive_checks_enabled":"1",
			"check_command":"dummy_command2"
	          }
	  }
    '''
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-o", "--host",action="store", type="string", dest="host",help="host option")
    parser.add_option("-i", "--ip",action="store", type="string", dest="ip",help="ip address option")
    parser.add_option("-u", "--url",action="store", type="string", dest="url",help="url option")
    parser.add_option("-c", action="store_true", dest="iscreate",help="create option")
    parser.add_option("-m", action="store_true", dest="ismonitor",help="monitor option")
    
    options, args = parser.parse_args()

    logger.info('iscreate=%s' % (options.iscreate))
    logger.info('ismonitor=%s' % (options.ismonitor))
    isUsingLinux = utils.isUsingLinux
    if (isUsingLinux):
	if (options.url):
	    if (options.host):
		if (options.ip):
		    if (options.iscreate):
			logger.info('Create mode !!!')
			payload = utils.SmartObject()

			payload.oper = "login"
			payload.username = __username__
			payload.password = __password__
			payload.target = "nagios.cfg"
			payload.cfg = "%s_nagios2" % (options.host)
			payload.partitions = "awk '{print $4}' /proc/partitions | sed -e '/name/d' -e '/^$/d' -e '/[1-9]/!d'"
			
			host1 = utils.SmartObject()
			host1.use = "generic-host"
			host1.host_name = options.host
			host1.alias = options.host
			host1.address = options.ip
			payload.host1 = host1.__dict__
			
			command1 = utils.SmartObject()
			command1.command_name = "dummy_command_%s" % (options.host)
			command1.command_line = "echo \"0\""
			payload.command1 = command1.__dict__
			
			services = ["CPU Load","Current Users","PING","SSH","Total Processes","Zombie Processes"]

			if (payload.partitions):
			    logger.info('1. payload.partitions=%s' % (payload.partitions))
			    results = utils.shellexecute(payload.partitions)
			    logger.info('2 results=%s' % (results))
			    partition_names = [str(r).strip() for r in results] if (utils.isList(results)) else results
			    logger.info('3 payload.partition_names=%s' % (payload.partition_names))
			    for partition in partition_names:
				services.append(partition)

			count = 1
			for svc in services:
			    service = utils.SmartObject()
			    service.use = "generic-service"
			    service.host_name = options.host
			    service.service_description = svc
			    service.active_checks_enabled = "0"
			    service.passive_checks_enabled = "1"
			    service.check_command = command1.command_name
			    payload['service%s' % (count)] = service.__dict__
			    count += 1

			headers = {'Content-Type':'application/json', 'Accept':'application/json'}
			r = requests.post('%s/nsca/nagios/create/config' % (options.url),data=simplejson.dumps(payload.__dict__), headers=headers)
			logger.debug('r.status_code=%s' % (r.status_code))
		    elif (options.ismonitor):
			logger.info('monitor mode !!!')
		    else:
			logger.error('Cannot determine what you want me to do ?!?')
		else:
		    logger.error('Cannot the ip (-i) you want me to use ?!?')
	    else:
		logger.error('Cannot the host (-h) you want me to use ?!?')
	else:
	    logger.error('Cannot the url (-u) you want me to use ?!?')
    else:
	logger.error('Linux is required ?!?')
    