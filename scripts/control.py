#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script to control homesite server.
'''
import argparse
import datetime
import os
import subprocess
import sys
# Django web utils
from django_web_utils import system_utils


def _log(text=''):
    print(text, file=sys.stdout)
    sys.stdout.flush()


def _err(text=''):
    print(text, file=sys.stderr)
    sys.stderr.flush()


def _exec(*args):
    _log('>>> %s' % ' '.join(args))
    shell = len(args) == 1
    p = subprocess.run(args, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, shell=shell)
    sys.stdout.flush()
    sys.stderr.flush()
    return p.returncode


class Controller():
    USER = 'homesite'
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(os.path.expanduser(__file__))))
    TEMP_DIR = '%s/temp' % BASE_DIR
    DUMPS_DIR = '%s/dbdumps' % BASE_DIR
    LOG_PATH = '%s/startup.log' % TEMP_DIR
    UWSGI_PID = '%s/uwsgi.pid' % TEMP_DIR
    USWGI_INI = '%s/scripts/uwsgi.ini' % BASE_DIR

    def __init__(self):
        pass

    def run(self):
        _log('---- Homesite control ----')
        # parse args
        parser = argparse.ArgumentParser(description=__doc__.strip())
        parser.add_argument('action', choices=['start', 'stop', 'restart', 'dump', 'update'], help='Action to run.')
        args = parser.parse_args()
        # Check user
        user_name = os.environ['USER']
        if user_name != self.USER:
            system_utils.run_as(self.USER)
        # Write initial info in log
        now = datetime.datetime.now()
        _log('Started on %s by user %s.' % (now.strftime('%Y-%m-%d %H:%M:%S'), user_name))
        # Check current dir
        os.chdir(self.BASE_DIR)
        sys.path.append(self.BASE_DIR)
        # Run action
        if args.action in ('dump', 'update'):
            self.dump()
        if args.action == 'update':
            self.update()
        if args.action in ('start', 'restart', 'stop', 'update'):
            self.stop()
        if args.action in ('start', 'restart', 'update'):
            self.start()
        sys.exit(0)

    def dump(self):
        _log('\n---- Dumping database ----')
        import settings
        dump_cmd = None
        if hasattr(settings, 'DATABASES') and settings.DATABASES.get('default'):
            dbs = settings.DATABASES.get('default')
            now = datetime.datetime.now()
            if 'sqlite' in dbs.get('ENGINE'):
                if dbs.get('NAME'):
                    db_path = dbs.get('NAME')
                dump_cmd = 'cp "%s" "%s/%s.db"' % (db_path, self.DUMPS_DIR, now.strftime('%Y-%m-%d_%H-%M-%S'))
            elif 'mysql' in dbs.get('ENGINE'):
                # MySQL
                dump_cmd = 'mysqldump -u %s %s %s --ignore-table=homesite.django_session > "%s/%s.sql"' % (
                    dbs.get('USER', 'root'),
                    '-p"%s"' % dbs['PASSWORD'] if dbs.get('PASSWORD') else '',
                    dbs.get('NAME', 'homesite'),
                    self.DUMPS_DIR,
                    now.strftime('%Y-%m-%d_%H-%M-%S'),
                )
            else:
                _err('The database engine is not handled.')
                sys.exit(1)
        if dump_cmd:
            if not os.path.exists(self.DUMPS_DIR):
                os.makedirs(self.DUMPS_DIR)
            rc = _exec(dump_cmd)
            if rc != 0:
                sys.exit(rc)
        else:
            _log('No database configured, dump command ignored.')

    def update(self):
        _log('\n---- Updating server ----')
        rc = _exec('git', 'pull', '--recurse-submodules')
        if rc != 0:
            sys.exit(rc)

    def stop(self):
        _log('\n---- Stopping server ----')
        rc = _exec('pkill', '-U', self.USER, '-9', '-f', '--', 'uwsgi --ini %s' % self.USWGI_INI)
        _log('pkill return code: %s' % rc)

    def start(self):
        _log('\n---- Starting server ----')
        if not os.path.exists(self.TEMP_DIR):
            os.makedirs(self.TEMP_DIR)
        if 'UWSGI_ORIGINAL_PROC_NAME' in os.environ:
            del os.environ['UWSGI_ORIGINAL_PROC_NAME']
        if 'UWSGI_RELOADS' in os.environ:
            del os.environ['UWSGI_RELOADS']
        os.execl('/usr/bin/uwsgi', 'uwsgi', '--ini', '%s' % self.USWGI_INI)


if __name__ == '__main__':
    controller = Controller()
    controller.run()
