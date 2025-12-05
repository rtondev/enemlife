#!/bin/bash
cd /root/enemlife
source venv/bin/activate
exec gunicorn --bind 0.0.0.0:7000 --workers 4 --timeout 120 wsgi:app

