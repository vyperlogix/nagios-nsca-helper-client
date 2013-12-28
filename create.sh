#!/bin/bash

if [ -f /root/bin/PYTHONPATH ]; then
	. /root/bin/PYTHONPATH
fi

python ./nsca-helper-client.py -o "vyperlogix3" -i "168.61.41.53" -u "http://vyperlogix1.cloudapp.net:15667" -c

