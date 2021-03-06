#!/bin/bash
cd src
tester=${isLocal:-no}
echo "Tester is"
echo $tester
if [ "$tester" != "yes" ]; then
	gunicorn app:app --access-logfile "-" --log-syslog --daemon
	echo “RUNNING APP AS DAEMON, for external Deployment.“
	unset tester
	python worker.py
else
	gunicorn app:app --access-logfile "-" --log-syslog --daemon
	echo “running as daemon with kill sequence, for local deployment.“
	unset tester
	python worker.py
	kill -9 `ps aux |grep gunicorn |grep app | awk '{ print $2 }'`
fi
