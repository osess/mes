from django.core.handlers.wsgi import WSGIHandler

import os
import sys

from os.path import abspath, dirname, join
from site import addsitedir

from django.conf import settings

import pinax.env

# setup the environment for Django and Pinax
pinax.env.setup_environ(__file__)

sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "thirdparty"))
# set application for WSGI processing
application = WSGIHandler()
