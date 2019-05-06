#!/bin/sh
set -e

if [ "$ENVIRONMENT_NAME" = "development" ]; then
    until python /postgres_check.py; do
      echo $?
      >&2 echo "Postgres is unavailable - sleeping"
      sleep 1
    done

    >&2 echo "Postgres is up - continuing"
fi

if [ "$IS_CELERY" != "yes" ]; then

    if [ "$PERFORM_MIGRATE" = "yes" ]; then
        python manage.py migrate
    fi

    if [ "$ENVIRONMENT_NAME" = "production" ]; then
        python manage.py collectstatic --noinput
    fi

    /uwsgi-nginx-entrypoint.sh
fi

exec "$@"
