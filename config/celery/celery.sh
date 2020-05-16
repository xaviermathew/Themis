#!/usr/bin/env bash

VIRTUALENV_BIN=/home/ubuntu/virtual_env/themis/bin
cd /home/ubuntu/Themis
source $VIRTUALENV_BIN/activate && source $VIRTUALENV_BIN/postactivate

CMD=$(cat <<COMMAND_SUFFIX
    2
	-A themis.core
    --pidfile=pids/celery/%N.pid
    --hostname=celery%i@%h
	-l INFO
	--logfile=logs/celery/%N.log
    --without-gossip --without-mingle --without-heartbeat
    -Q:1 T_crawl_feed,T_process_article,T_crawl_twitter -c:1 1
    -Q:2 T_process_tweet -c:2 3
COMMAND_SUFFIX
)

echo "stopping celery"
DJANGO_SETTINGS_MODULE=themis.core.settings celery multi stop $CMD
echo "waiting for 3s"
sleep 3
echo "starting celery"
DJANGO_SETTINGS_MODULE=themis.core.settings celery multi restart $CMD
