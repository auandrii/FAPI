#!/bin/sh
uvicorn main:app --host 0.0.0.0 &
celery -A main.celery_app worker --loglevel=info &
wait