#!/bin/bash

set -e

# Проверяем, используется ли PostgreSQL
if [ -n "$POSTGRES_DB" ]; then
    echo "Waiting for PostgreSQL to be ready..."
    
    # Ожидаем готовности PostgreSQL
    until python -c "import psycopg2; psycopg2.connect(host='$POSTGRES_HOST', port='$POSTGRES_PORT', user='$POSTGRES_USER', password='$POSTGRES_PASSWORD', dbname='$POSTGRES_DB')" 2>/dev/null; do
      echo "PostgreSQL is unavailable - sleeping"
      sleep 1
    done
    
    echo "PostgreSQL is up - executing migrations"
fi

# Применяем миграции
python lr4/manage.py makemigrations --noinput || true
python lr4/manage.py migrate --noinput

# Собираем статические файлы
python lr4/manage.py collectstatic --noinput || true

echo "Starting server..."

exec "$@"

