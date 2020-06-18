#!/usr/bin/env bash

VIRTUALENV_BIN=/home/ubuntu/virtual_env/mnemonic/bin
cd /home/ubuntu/Mnemonic
source $VIRTUALENV_BIN/activate && source $VIRTUALENV_BIN/postactivate

echo "${1-start}ing celery"
DJANGO_SETTINGS_MODULE=mnemonic.core.settings $VIRTUALENV_BIN/celery multi ${1} \
    2 \
	-A mnemonic.core \
    --pidfile=pids/celery/%N.pid \
    --hostname=celery%i@%h \
	-l INFO \
	--logfile=logs/celery/%N.log \
    --without-gossip --without-mingle --without-heartbeat \
    -Q:1 T_crawl_feed,T_process_article -c:1 2 \
    -Q:2 T_crawl_twitter,T_process_tweet -c:2 2
