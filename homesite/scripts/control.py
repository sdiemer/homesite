#!/usr/bin/env python3
'''
Script to control homesite server.
'''
from pathlib import Path
import argparse
import datetime
import os
import subprocess
import sys


USER = 'homesite'
OPT_DIR = Path('/opt/homesite')
TMP_DIR = OPT_DIR / 'data/tmp'
USWGI_INI = OPT_DIR / 'repo/deployment/uwsgi.ini'
MAX_DUMPS = 10


def _run(*args):
    print(f'>>> {" ".join(args)}')
    p = subprocess.run(args, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()
    return p.returncode


def main():
    print('---- Homesite control ----')
    # parse args
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument(
        'action',
        choices=['start', 'stop', 'restart', 'manage', 'update'],
        help='Action to run.'
    )
    parser.add_argument(
        '--autoreload',
        action='store_true',
        help='For start and restart actions, enable the UWSGI auto-reload mode.'
    )
    parser.add_argument(
        'args', nargs=argparse.REMAINDER,
        help='Arguments for the "manage" action. Use no arguments to display the list of available commands.'
    )
    args = parser.parse_args()
    # Write initial info in log
    now = datetime.datetime.now()
    print(f'Started on {now.strftime("%Y-%m-%d %H:%M:%S")}.')
    # Check user
    if os.getuid() != 0:
        print('This script must be run as root.')
        sys.exit(1)
    # Run action
    if args.action in ('start', 'restart', 'stop'):
        stop()
    if args.action in ('start', 'restart'):
        start(args.autoreload)
    if args.action == 'manage':
        manage(*args.args)
    if args.action == 'update':
        update()
    sys.exit(0)


def manage(*args):
    print('---- Starting manage ----')
    os.execl(
        '/usr/sbin/runuser', 'runuser', '-u', USER, '--',
        str(OPT_DIR / 'venv/bin/django-manage'), *args
    )


def update():
    print('---- Updating server ----')
    os.execl('/bin/bash', 'bash', str(OPT_DIR / 'deployment/setup.sh'))


def stop():
    print('---- Stopping server ----')
    rc = _run('pkill', '-U', USER, '-9', '-f', '--', f'uwsgi --ini {USWGI_INI}')
    print(f'pkill return code: {rc}')


def start(autoreload):
    print('---- Starting server ----')
    if 'UWSGI_ORIGINAL_PROC_NAME' in os.environ:
        del os.environ['UWSGI_ORIGINAL_PROC_NAME']
    if 'UWSGI_RELOADS' in os.environ:
        del os.environ['UWSGI_RELOADS']
    _run('runuser', '-u', USER, '--', 'mkdir', '-p', str(TMP_DIR))
    cmd = ['uwsgi', '--ini', str(USWGI_INI)]
    if autoreload:
        cmd.extend(['--py-autoreload', '1'])
    os.execl('/usr/sbin/runuser', 'runuser', '-u', USER, '--', *cmd)


if __name__ == '__main__':
    main()
