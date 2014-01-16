#!/usr/bin/python
import os, sys

_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DJANGO_DIR = os.path.join(_PROJECT_DIR, 'src/alfanous-django')

sys.path.insert(0, _PROJECT_DIR)
sys.path.insert(0, DJANGO_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
