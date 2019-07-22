#!/usr/bin/env bash

NAME="FEVI-BACKEND"
DJANGODIR=/home/ubuntu/backend/
USER=ubuntu
GROUP=ubuntu

echo "starting $NAME"

cd $DJANGODIR
#source $DJANGODIR/venv/bin/activate
export PATH=$PATH:~/.local/bin
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
cd $DJANGODIR/fevi/

echo "before gunicorn"
exec celery -A fevi worker -l info -n first
echo "after gunicorn"
