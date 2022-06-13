#!/usr/bin/env python3
"""
WSGI config.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""
from pathlib import Path
import os
import sys

if '' in sys.path:
    sys.path.remove('')
if '.' in sys.path:
    sys.path.remove('.')

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homesite.settings')

from django.core.wsgi import get_wsgi_application  # NOQA
application = get_wsgi_application()
