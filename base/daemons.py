#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
# Django
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


def CAN_ACCESS(request):
    return request.user.is_superuser


def CAN_CONTROL(request):
    return request.user.is_superuser


DAEMONS = [
    dict(
        group='base', name='django', label='Django', no_commands=True, only_log=True,
        log_path=os.path.join(settings.TMP_DIR, 'django.log'),
        help_text=_('This is not a daemon, but only a log file.')
    ),
]
GROUPS = [
    dict(name='base', label=_('Base daemons')),
]
