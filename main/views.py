#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import subprocess
# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
# Django web utils
from django_web_utils.monitoring import sysinfo
# homesite
import homesite


def get_ip(request):
    return HttpResponse(request.META.get('REMOTE_ADDR', '0.0.0.0'), content_type='text/plain')


@login_required
def info(request):
    # Server info
    tplt_args = sysinfo.get_system_info(module=homesite)

    tplt_args['section'] = 'info'
    return render(request, 'info.html', tplt_args)


@login_required
def ark(request):
    # ARK server management
    tplt_args = dict()

    if request.method == 'POST':
        cmd = ['python3', os.path.join(homesite.__path__[0], 'scripts', 'ark_server.py'), request.user.username]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        out, err = p.communicate()
        out = str(out, 'utf-8') if out else 'No stdout.'
        err = str(err, 'utf-8') if err else 'No stderr.'
        msg_pattern = '%%s\nStdout:\n%s\nStderr:\n%s' % (out.strip(), err.strip())
        if p.returncode == 0:
            messages.success(request, msg_pattern % _('Command successfully executed.'))
        else:
            messages.success(request, msg_pattern % _('Command failed.'))
        return HttpResponseRedirect(reverse('ark'))

    # Get ps output
    cmd = 'ps aux | grep ShooterGameServer | grep -v grep'
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    ps_out = str(out, 'utf-8') if out else ''
    if err:
        ps_out += '\n'
        ps_out += str(err, 'utf-8')
    if not ps_out:
        ps_out = _('Server is not running.')
    else:
        ps_out = '>>> ' + cmd + '\n' + ps_out
    tplt_args['ps_out'] = ps_out

    # Get log content
    path = os.path.abspath(os.path.expanduser('~/ark_server.log'))
    log = _('Log file does not exists.')
    if os.path.isfile(path):
        with open(path, 'r') as fd:
            log = fd.read()
        if not log:
            log = _('Log file is empty.')
    tplt_args['log'] = log

    tplt_args['section'] = 'ark'
    return render(request, 'ark.html', tplt_args)
