#!/usr/bin/env bash

source activate && source postactivate

exec gunicorn themis.core.wsgi \
  --name "Themis" \
  --workers 1 \
  --bind=0.0.0.0:8000 \
  --log-level=info \
  --timeout=30 \
  --log-file=logs/gunicorn.log \
  --env DJANGO_SETTINGS_MODULE=themis.core.settings
