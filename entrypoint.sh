#!/bin/sh
echo "Flush the manage.py command it any"

while ! python manage.py flush --settings=api.api.settings.prod --no-input 2>&1; do
  echo "Flusing django manage command"
  sleep 3
done

echo "Migrate the Database at startup of project"

echo api/api/settings/prod.py

# Wait for few minute and run db migraiton
while ! python manage.py migrate --settings=api.api.settings.prod  2>&1; do
   echo "Migration is in progress status"
   sleep 3
done


gunicorn api.api.wsgi:application --bind 0.0.0.0:8001
exec "$@"
