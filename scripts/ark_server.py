#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to start ARK server.
"""
import datetime
import os
import subprocess
import sys
import time
# Django web utils
from django_web_utils.daemon.daemonization import daemonize

LOG_PATH = os.path.abspath(os.path.expanduser('~/ark_server.log'))
LOG_BU_PATH = LOG_PATH[:-4] + '.back.log'
ARK_DUMP_PATH = os.path.abspath(os.path.expanduser('~/ark_dump.sh'))
ARK_UPDATE_PATH = os.path.abspath(os.path.expanduser('~/ark_update.sh'))
ARK_START_PATH = os.path.abspath(os.path.expanduser('~/ark_server.sh'))


def _log(text=''):
    print('%s\n' % text, file=sys.stdout)
    sys.stdout.flush()


def _exec(*args):
    print('>>> %s\n' % ' '.join(args), file=sys.stdout)
    sys.stdout.flush()
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, shell=False)
    p.communicate()
    print('', file=sys.stdout)
    sys.stdout.flush()
    return p.returncode


if __name__ == '__main__':
    now = datetime.datetime.now()
    # Prepare log file path
    if os.path.exists(LOG_PATH):
        if os.path.exists(LOG_BU_PATH):
            os.remove(LOG_BU_PATH)
        os.rename(LOG_PATH, LOG_BU_PATH)
    # Daemonize
    wd = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    daemonize(redirect_to=LOG_PATH, rundir=wd)
    sys.path.append(wd)
    # Write initial info in log
    user_id = sys.argv[1] if len(sys.argv) > 1 else '?'
    _log('Started on %s by user %s.\n' % (now.strftime('%Y-%m-%d %H:%M:%S'), user_id))
    _log('---- Stopping server ----')
    rc = _exec('pkill', '-f', '--', 'ShooterGameServer')
    _log('pkill return code: %s' % rc)
    time.sleep(2)
    _log('---- Backuping saves ----')
    rc = _exec('/bin/bash', ARK_DUMP_PATH)
    if rc != 0:
        print('Command failed.', file=sys.stdout)
        sys.exit(1)
    _log('---- Update server ----')
    rc = _exec('/bin/bash', ARK_UPDATE_PATH)
    if rc != 0:
        print('Command failed.', file=sys.stdout)
        sys.exit(1)
    _log('---- Starting server ----')
    os.execl('/bin/bash', 'bash', ARK_START_PATH)
