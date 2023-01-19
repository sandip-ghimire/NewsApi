#!/bin/bash

(DJANGO_SETTINGS_MODULE=newsfinder.settings
DJANGO_WSGI_MODULE=newsfinder.wsgi

cd /app
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

exec venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
--workers 3 \
--bind=unix:/app/venv/gunicorn.sock \
--log-level=debug \
--log-file=/var/log/gunicorn_error-log \
--access-logfile=/var/log/gunicorn_access-log) &
nginx -g "daemon off;"