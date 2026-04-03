#!/bin/sh
set -e

python init_db.py
exec flask run --host=0.0.0.0 --port=5000
