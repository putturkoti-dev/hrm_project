#!/usr/bin/env bash

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser \
  --noinput \
  --username admin \
  --email admin@gmail.com || true

python manage.py collectstatic --noinput