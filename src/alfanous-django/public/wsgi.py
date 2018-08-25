#!/usr/bin/eval PYTHON_VERSION=2.7 python

import os, sys

_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DJANGO_DIR = os.path.join(_PROJECT_DIR, 'src/alfanous-django')

sys.path.insert(0, _PROJECT_DIR)
sys.path.insert(0, DJANGO_DIR)

sys.path.append('/dev1/src/alfanous-django/alf/Lib/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = "settings"


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()