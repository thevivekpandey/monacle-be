#!/usr/bin/env bash
sudo apt-get install supervisor

# Creating celery worker
mkdir -p /home/ubuntu/log/fevi_backend/
mkdir -p /home/ubuntu/log/celery_beat/
mkdir -p /home/ubuntu/log/celery_worker/

# updating and starting supervisor
sudo cp supervisor_config/fevi_backend_process.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update