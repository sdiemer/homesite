#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to start ARK server.

Usage: <script name> [restart|stop] [<user name>]
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
    print(text, file=sys.stdout)
    sys.stdout.flush()


def _exec(*args):
    _log('>>> %s' % ' '.join(args))
    shell = len(args) == 1 and '|' in args[0]
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, shell=shell)
    p.communicate()
    sys.stdout.flush()
    return p.returncode


if __name__ == '__main__':
    now = datetime.datetime.now()
    # Check that the script is not running
    _log('Checking that the script is not currently running...')
    rc = _exec('ps aux | grep -v grep | grep -v " %s " | grep %s' % (os.getpid(), os.path.basename(__file__)))
    if rc == 0:
        print('The ARK startup script is already running.', file=sys.stderr)
        sys.exit(1)
    _log('OK')
    # Get command
    action = sys.argv[1] if len(sys.argv) > 1 else 'restart'
    if action not in ('restart', 'stop'):
        print('Invalid action requested.', file=sys.stderr)
        sys.exit(1)
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
    user_id = sys.argv[2] if len(sys.argv) > 2 else '?'
    _log('Started on %s by user %s.' % (now.strftime('%Y-%m-%d %H:%M:%S'), user_id))
    _log('\n---- Stopping server ----\n')
    rc = _exec('pkill', '-f', '--', 'ShooterGameServer')
    _log('pkill return code: %s' % rc)
    if action == 'stop':
        sys.exit(0)
    time.sleep(2)
    _log('\n---- Backuping saves ----\n')
    rc = _exec('/bin/bash', ARK_DUMP_PATH)
    if rc != 0:
        print('Command failed.', file=sys.stdout)
        sys.exit(1)
    _log('\n---- Update server ----\n')
    rc = _exec('/bin/bash', ARK_UPDATE_PATH)
    if rc != 0:
        print('Command failed.', file=sys.stdout)
        sys.exit(1)
    _log('\n---- Starting server ----\n')
    os.execl('/bin/bash', 'bash', ARK_START_PATH)
