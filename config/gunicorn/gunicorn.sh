#!/usr/bin/env bash
VIRTUALENV_BIN=/home/ubuntu/virtual_env/mnemonic/bin
cd /home/ubuntu/Mnemonic
source $VIRTUALENV_BIN/activate && source $VIRTUALENV_BIN/postactivate

$VIRTUALENV_BIN/gunicorn mnemonic.core.wsgi \
  --name "Mnemonic" \
  --workers 1 \
  --bind=0.0.0.0:8000 \
  --log-level=info \
  --timeout=30 \
  --log-file=logs/gunicorn.log \
  --env DJANGO_SETTINGS_MODULE=mnemonic.core.settings
