#!/bin/sh
set -e

echo "[entrypoint] Attente de MySQL..."
until python -c "
import os, pymysql
pymysql.connect(
    host='db',
    user=os.environ['MYSQL_USER'],
    password=os.environ['MYSQL_PASSWORD'],
    database=os.environ['MYSQL_DATABASE']
).close()
" 2>/dev/null; do
  echo "[entrypoint] MySQL pas encore pret, retry dans 2s..."
  sleep 2
done
echo "[entrypoint] MySQL pret."

python init_db.py
exec flask run --host=0.0.0.0 --port=5000
