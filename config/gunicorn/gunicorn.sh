#!/usr/bin/env bash
VIRTUALENV_BIN=/home/ubuntu/virtual_env/themis/bin
cd /home/ubuntu/Themis
source $VIRTUALENV_BIN/activate && source $VIRTUALENV_BIN/postactivate

$VIRTUALENV_BIN/gunicorn themis.core.wsgi \
  --name "Themis" \
  --workers 1 \
  --bind=0.0.0.0:8000 \
  --log-level=info \
  --timeout=30 \
  --log-file=logs/gunicorn.log \
  --env DJANGO_SETTINGS_MODULE=themis.core.settings
