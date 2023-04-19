#! /usr/bin/env sh
set -e
celery -A tasks worker --loglevel=INFO --concurrency=10