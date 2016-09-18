#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to manage ARK server.

Usage: <script name> [restart|stop|dump|update|validate] [<user name>]

To allow another user to run this script:
sudo visudo
homesite ALL=(ALL) NOPASSWD: /home/homesite/homesite/scripts/ark_server.py
"""
import datetime
import os
import subprocess
import sys
import time
import shutil
# Django web utils
from django_web_utils.daemon.daemonization import daemonize
from django_web_utils import system_utils

USER = 'steam'
ARK_DIR = '/home/steam/ark'
ARK_GAME_DIR = '%s/Ark_Survival_Evolved' % ARK_DIR
ARK_DUMP_DIR = '%s/dumps' % ARK_DIR
LOG_PATH = '%s/ark_server.log' % ARK_DIR
LOG_BU_PATH = LOG_PATH[:-4] + '.back.log'


def _log(text=''):
    print(text, file=sys.stdout)
    sys.stdout.flush()


def _err(text=''):
    print(text, file=sys.stderr)
    sys.stderr.flush()


def _exec(*args):
    _log('>>> %s' % ' '.join(args))
    shell = len(args) == 1
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, shell=shell)
    p.communicate()
    sys.stdout.flush()
    sys.stderr.flush()
    return p.returncode


if __name__ == '__main__':
    now = datetime.datetime.now()
    # Check that the script is not running
    _log('Checking that the script is not currently running...')
    rc = _exec('ps aux | grep -v grep | grep -v " %s " | grep -v " %s " | grep "%s"' % (os.getpid(), os.getppid(), __file__))
    if rc == 0:
        _err('The script is already running.')
        sys.exit(1)
    _log('OK')
    # Get command
    action = sys.argv[1] if len(sys.argv) > 1 else 'restart'
    actions = ('restart', 'stop', 'dump', 'update', 'validate')
    if action not in actions:
        _err('Invalid action requested. Possible actions are %s.' % ', '.join(actions))
        sys.exit(1)
    # Check user
    user_name = os.environ['USER']
    if os.environ['USER'] != USER:
        system_utils.run_as(USER)
    # Prepare log file path
    if not os.path.exists(ARK_DIR):
        os.makedirs(ARK_DIR)
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

    if action in ('restart', 'stop'):
        _log('\n---- Stopping server ----')
        rc = _exec('pkill', '-U', USER, '-f', '--', 'ShooterGameServer')
        _log('pkill return code: %s' % rc)
        if action == 'stop':
            sys.exit(0)
        time.sleep(2)

    _log('\n---- Backuping saves ----')
    if not os.path.exists(ARK_DUMP_DIR):
        os.makedirs(ARK_DUMP_DIR)
    dump_path = os.path.join(ARK_DUMP_DIR, 'Saved_%s' % now.strftime('%Y-%m-%d'))
    if os.path.exists(dump_path):
        _log('Saves already dumped today.')
    else:
        shutil.copytree(os.path.join(ARK_GAME_DIR, 'ShooterGame', 'Saved'), dump_path)
        _exec('chmod', '-R', '777', dump_path)
        _log('Backup done.')

    if action in ('restart', 'update', 'validate'):
        _log('\n---- Update server ----')
        app_update = '376030 validate' if action == 'validate' else '376030'
        rc = _exec('/home/steam/steamcmd/steamcmd.sh', '+login anonymous', '+force_install_dir', ARK_GAME_DIR, '+app_update', app_update, '+quit')
        if rc != 0:
            _log('Update failed.')
            sys.exit(1)
        else:
            _log('Update done.')

    if action == 'restart':
        _log('\n---- Starting server ----')
        os.execl('/bin/bash', 'bash', 'cd %s && TheIsland?listen?SessionName=akiserver?ServerPassword=1234lol?ServerAdminPassword=qsdfghjklm?MaxPlayers=12?XPMultiplier=3?HarvestAmountMultiplier=3?TamingSpeedMultiplier=3?PlayerCharacterWaterDrainMultiplier=0.7?PlayerCharacterFoodDrainMultiplier=0.7?ShowMapPlayerLocation=True?allowThirdPersonPlayer=True?alwaysNotifyPlayerJoined=True?alwaysNotifyPlayerLeft=True?ServerCrosshair=True -server -log' % os.path.join(ARK_GAME_DIR, 'ShooterGame', 'Binaries', 'Linux'))
