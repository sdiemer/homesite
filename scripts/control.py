#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script to control homesite server.
'''
import argparse
import datetime
import difflib
import os
import re
import subprocess
import sys
import traceback
# Django web utils
from django_web_utils import system_utils
from django_web_utils.scripts_utils import log, log_error, log_warning, log_info


def _exec(*args):
    log('>>> %s' % ' '.join(args))
    shell = len(args) == 1
    p = subprocess.run(args, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, shell=shell)
    sys.stdout.flush()
    sys.stderr.flush()
    return p.returncode


class Controller():
    USER = 'homesite'
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(os.path.expanduser(__file__))))
    TMP_DIR = '%s/data/temp' % BASE_DIR
    DUMPS_DIR = '%s/data/dbdumps' % BASE_DIR
    LOG_PATH = '%s/data/logs/startup.log' % TMP_DIR
    UWSGI_PID = '%s/data/temp/uwsgi.pid' % TMP_DIR
    USWGI_INI = '%s/scripts/uwsgi.ini' % BASE_DIR
    MAX_DUMPS = 10

    def __init__(self):
        pass

    def run(self):
        log_info('---- Homesite control ----')
        # parse args
        parser = argparse.ArgumentParser(description=__doc__.strip())
        parser.add_argument('action', choices=['start', 'stop', 'restart', 'dump', 'update', 'createuser'], help='Action to run.')
        parser.add_argument('target', nargs='?', default=None, help='Target of action. Target is the file path when using dump action. Target should be "<username>:<password>:<role>" when using "createuser" action (password and role are not required; role can be "regular", "staff" or "supersuer").')
        args = parser.parse_args()
        # Check user
        user = os.environ['USER']
        if user != self.USER:
            system_utils.run_as(self.USER)
        # Write initial info in log
        now = datetime.datetime.now()
        log('Started on %s by user %s.' % (now.strftime('%Y-%m-%d %H:%M:%S'), user))
        # Check current dir
        os.chdir(self.BASE_DIR)
        sys.path.append(self.BASE_DIR)
        # Run action
        if args.action in ('dump', 'update'):
            self.dump(args.target)
        if args.action == 'update':
            self.update()
        if args.action in ('start', 'restart', 'stop', 'update'):
            self.stop()
        if args.action in ('start', 'restart', 'update'):
            self.start()
        if args.action == 'createuser':
            self.create_user(args.target)
        sys.exit(0)

    def dump(self, path=None):
        log_info('---- Dumping database ----')
        import settings
        dump_cmd = None
        if hasattr(settings, 'DATABASES') and settings.DATABASES.get('default'):
            dbs = settings.DATABASES.get('default')
            now = datetime.datetime.now()
            if 'sqlite' in dbs.get('ENGINE'):
                if dbs.get('NAME'):
                    db_path = dbs.get('NAME')
                dump_path = path or '%s/%s.db' % self.DUMPS_DIR, now.strftime('%Y-%m-%d_%H-%M-%S')
                dump_cmd = 'cp "%s" "%s"' % (db_path, dump_path)
            elif 'mysql' in dbs.get('ENGINE'):
                dump_path = path or '%s/%s.sql' % self.DUMPS_DIR, now.strftime('%Y-%m-%d_%H-%M-%S')
                dump_cmd = 'mysqldump -u %s %s %s --ignore-table=homesite.django_session > "%s"' % (
                    dbs.get('USER', 'root'),
                    '-p"%s"' % dbs['PASSWORD'] if dbs.get('PASSWORD') else '',
                    dbs.get('NAME', 'homesite'),
                    dump_path,
                )
            else:
                log_error('The database engine is not handled.')
                sys.exit(1)
        if dump_cmd:
            if not os.path.exists(self.DUMPS_DIR):
                os.makedirs(self.DUMPS_DIR)
            os.chmod(self.DUMPS_DIR, 0o700)
            rc = _exec(dump_cmd)
            if rc != 0:
                sys.exit(rc)
            # Remove old dumps
            log('Searching for old database dump to remove...')
            dumps = list()
            for name in os.listdir(self.DUMPS_DIR):
                if name.endswith('.sql') or name.endswith('.db'):
                    path = os.path.join(self.DUMPS_DIR, name)
                    dumps.append((os.path.getmtime(path), path))
            if dumps:
                dumps.sort()
                while len(dumps) >= self.MAX_DUMPS:
                    path = dumps.pop(0)[1]
                    log('Removing old database dump "%s".' % path)
                    os.remove(path)
        else:
            log('No database configured, dump command ignored.')

    def update(self):
        log_info('---- Updating server ----')
        rc = _exec('git', 'pull', '--recurse-submodules')
        if rc != 0:
            sys.exit(rc)

    def stop(self):
        log_info('---- Stopping server ----')
        rc = _exec('pkill', '-U', self.USER, '-9', '-f', '--', 'uwsgi --ini %s' % self.USWGI_INI)
        log('pkill return code: %s' % rc)

    def start(self):
        log_info('---- Starting server ----')
        if not os.path.exists(self.TMP_DIR):
            os.makedirs(self.TMP_DIR)
        if 'UWSGI_ORIGINAL_PROC_NAME' in os.environ:
            del os.environ['UWSGI_ORIGINAL_PROC_NAME']
        if 'UWSGI_RELOADS' in os.environ:
            del os.environ['UWSGI_RELOADS']
        os.execl('/usr/bin/uwsgi', 'uwsgi', '--ini', '%s' % self.USWGI_INI)

    def create_user(self, credential=None):
        if not credential:
            log('Please provide at least a username.')
            sys.exit(1)
        splitted = credential.split(':')
        username = splitted[0].strip()
        password = splitted[1] if len(splitted) > 1 else None
        role = splitted[2] if len(splitted) > 2 else None
        if not username:
            log('Please provide at least a username.')
            sys.exit(1)
        log_info('---- Creating user account "%s" ----' % username)
        try:
            os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
            try:
                import django
                django.setup()
            except Exception as e:
                if 'Settings already configured' not in str(e):
                    raise
            from django.conf import settings
            from django.contrib.auth.models import User
            user_dict = settings.AUTHENTICATION_USERS.get(username)
            if user_dict:
                user = User(username=username, **user_dict)
                log('The user account already exists.')
            else:
                user = User(username=username, is_active=True)
            log('Updating user account password.')
            if not password:
                log_warning('The password is empty for user account "%s". The user account will not be usable to login. You can specify the password using the environment variable "PWD".' % username)
                user.password = ''
            else:
                if password == 'test':
                    log_warning('The user account "%s" password has been set to "%s", please change it as soon as possible.' % (username, password))
                user.set_password(password)
                log('Password updated.')
            log('Updating user account rights.')
            if '@' in username:
                user.email = username
            if role == 'superuser':
                user.is_staff = True
                user.is_superuser = True
            elif role == 'staff':
                user.is_staff = True
                user.is_superuser = False
            else:
                user.is_staff = False
                user.is_superuser = False
            log('Saving user account.')
            if not user.is_active:
                log_warning('The user account "%s" is disabled, to reactivate it, please edit the configuration file manually.' % username)
            user_dict = dict(
                is_active=user.is_active,
                is_staff=user.is_staff,
                is_superuser=user.is_superuser,
                email=user.email,
                password=user.password,
            )
            settings.AUTHENTICATION_USERS[username] = user_dict
            if os.path.exists(settings.OVERRIDE_PATH):
                with open(settings.OVERRIDE_PATH, 'r') as fo:
                    content = fo.read()
            else:
                content = ''
            users_repr = '\nAUTHENTICATION_USERS = {'
            for username, info in settings.AUTHENTICATION_USERS.items():
                users_repr += "\n    '%s': %s," % (username, info)
            users_repr += '\n}'
            new_content = re.sub(r'\nAUTHENTICATION_USERS\s*=\s*{.*\n}', users_repr, content, flags=re.DOTALL)
            if 'AUTHENTICATION_USERS' not in new_content:
                new_content += users_repr + '\n'
            if content != new_content:
                sys.stdout.writelines(difflib.unified_diff(content.splitlines(keepends=True), new_content.splitlines(keepends=True), fromfile='current settings "%s"' % settings.OVERRIDE_PATH, tofile='new settings'))
                with open(settings.OVERRIDE_PATH, 'w') as fo:
                    fo.write(new_content)
                log('User account saved.')
            else:
                log('No changes to save.')
        except Exception:
            log_warning('Error when creating user account. Error:\n%s' % traceback.format_exc())
        else:
            log('User account "%s" ready.' % username)


if __name__ == '__main__':
    controller = Controller()
    controller.run()
