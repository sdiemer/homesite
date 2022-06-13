#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script to control homesite server.
'''
from pathlib import Path
import argparse
import datetime
import os
import pwd
import subprocess
import sys


USER = 'homesite'
DATA_DIR = Path(f'/home/{USER}/homesite-data')
TMP_DIR = DATA_DIR / 'temp'
DUMPS_DIR = DATA_DIR / 'dbdumps'
STATIC_DIR = DATA_DIR / 'static'
PYTHON_DIR = Path('/opt/homesite')
USWGI_INI = PYTHON_DIR / 'homesite/scripts/uwsgi.ini'
MAX_DUMPS = 10


def _exec(*args):
    print('>>> %s' % ' '.join(args))
    shell = len(args) == 1
    p = subprocess.run(args, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, shell=shell)
    sys.stdout.flush()
    sys.stderr.flush()
    return p.returncode


def run():
    print('---- Homesite control ----')
    # parse args
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'update', 'shell', 'createsuperuser'], help='Action to run.')
    args = parser.parse_args()
    # Check user
    user = pwd.getpwuid(os.getuid()).pw_name
    if user != USER:
        print(f'Switching user to {USER}.')
        sys.stdout.flush()
        os.execl('/usr/sbin/runuser', 'runuser', '-u', USER, '--', *sys.argv)
        sys.exit(1)
    # Write initial info in log
    now = datetime.datetime.now()
    print(f'Started on {now.strftime("%Y-%m-%d %H:%M:%S")} by user {user}.')
    # Check current dir
    os.chdir(PYTHON_DIR)
    sys.path.pop(0)
    sys.path.append(str(PYTHON_DIR))
    # Run action
    if args.action == 'update':
        update()
    if args.action in ('start', 'restart', 'stop', 'update'):
        stop()
    if args.action in ('start', 'restart', 'update'):
        start()
    if args.action == 'shell':
        shell()
    if args.action == 'createsuperuser':
        createsuperuser()
    sys.exit(0)


def shell():
    print('---- Starting shell ----')
    os.execl('/usr/bin/python3', 'python3', str(PYTHON_DIR / 'homesite/manage.py'), 'shell')


def createsuperuser():
    print('---- Starting createsuperuser ----')
    os.execl('/usr/bin/python3', 'python3', str(PYTHON_DIR / 'simple_order/manage.py'), 'createsuperuser')


def update():
    print('---- Updating server ----')
    cmds = [
        ('find', '.', '-name', '*.pyc', '-type', 'f', '-delete'),
        ('find', '.', '-name', '__pycache__', '-type', 'd', '-delete'),
        ('git', 'fetch', '--recurse-submodules', '--all'),
        ('git', 'reset', '--hard', 'origin/main'),
        ('git', 'pull', '--recurse-submodules'),
    ]
    for cmd in cmds:
        rc = _exec(*cmd)
        if rc != 0:
            sys.exit(rc)


def stop():
    print('---- Stopping server ----')
    rc = _exec('pkill', '-U', USER, '-9', '-f', '--', 'uwsgi --ini %s' % USWGI_INI)
    print('pkill return code: %s' % rc)


def start():
    print('---- Checking static links ----')
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    if not (STATIC_DIR / 'admin').exists():
        print('Creating admin static link')
        import django
        _exec('ln', '-sfn', str(Path(django.__path__[0]) / 'contrib/admin/static/admin'), str(STATIC_DIR / 'admin'))
    if not (STATIC_DIR / 'monitoring').exists():
        print('Creating monitoring static link')
        import django_web_utils
        _exec('ln', '-sfn', str(Path(django_web_utils.__path__[0]) / 'monitoring/static/monitoring'), str(STATIC_DIR / 'monitoring'))
    if not (STATIC_DIR / 'file_browser').exists():
        print('Creating file_browser static link')
        import django_web_utils
        _exec('ln', '-sfn', str(Path(django_web_utils.__path__[0]) / 'file_browser/static/file_browser'), str(STATIC_DIR / 'file_browser'))
    if not (STATIC_DIR / 'homesite').exists():
        print('Creating homesite static link')
        _exec('ln', '-sfn', str(PYTHON_DIR / 'homesite/static/homesite'), str(STATIC_DIR / 'homesite'))

    print('---- Starting server ----')
    if 'UWSGI_ORIGINAL_PROC_NAME' in os.environ:
        del os.environ['UWSGI_ORIGINAL_PROC_NAME']
    if 'UWSGI_RELOADS' in os.environ:
        del os.environ['UWSGI_RELOADS']
    os.execl('/usr/bin/uwsgi', 'uwsgi', '--ini', '%s' % USWGI_INI)


if __name__ == '__main__':
    run()
