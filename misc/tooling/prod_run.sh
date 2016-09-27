#!/bin/bash

./manage.py migrate
uwsgi --ini uwsgi.ini
