#!/usr/bin/env bash

NAME="FEVI-BACKEND"
DJANGODIR=/home/ubuntu/backend
USER=ubuntu
GROUP=ubuntu
NUM_WORKERS=3

echo "starting $NAME"

cd $DJANGODIR
#source $DJANGODIR/venv/bin/activate
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
export PATH=$PATH:~/.local/bin
cd $DJANGODIR/fevi/
echo "before gunicorn"
exec gunicorn -w $NUM_WORKERS --timeout 60 --bind=0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=fevi.settings fevi.wsgi
echo "after gunicorn"
