#!/bin/sh
set -e

echo "==> マイグレーションファイルを確認しています..."
python manage.py makemigrations roadmap --noinput

echo "==> マイグレーションを適用しています..."
python manage.py migrate --noinput

if [ "$SEED_DATA" = "true" ]; then
  echo "==> サンプルデータを投入しています..."
  python manage.py seed_data
fi

echo "==> 起動します: $@"
exec "$@"
