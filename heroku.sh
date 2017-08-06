#!/bin/bash
cd src
tester=${isLocal:-no}
if [[ $tester != yes ]]
then
	gunicorn app:app --daemon
	echo “RUNNING APP AS DAEMON, for external Deployment.“
	unset tester
	python worker.py
else
	gunicorn app:app --daemon
	echo “running as daemon with kill sequence, for local deployment.“
	unset tester
	python worker.py
	kill -9 `ps aux |grep gunicorn |grep app | awk '{ print $2 }'`
fi
