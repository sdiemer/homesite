#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from mimetypes import MimeTypes
import logging
import os
import subprocess
# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
# Django web utils
from django_web_utils.monitoring import sysinfo
# homesite
import homesite

logger = logging.getLogger('homesite.base.views')


def get_ip(request):
    return HttpResponse(request.META.get('REMOTE_ADDR', '0.0.0.0'), content_type='text/plain')


@login_required
def info(request):
    # Server info
    tplt_args = sysinfo.get_system_info(module=homesite)

    tplt_args['section'] = 'info'
    return render(request, 'base/info.html', tplt_args)


@login_required
def munin(request):
    munin_url = reverse('munin_file', args=[settings.MUNIN_BASE])
    return render(request, 'base/munin.html', {
        'munin_url': munin_url,
        'section': 'munin',
    })


@login_required
def munin_file(request, path):
    if not path:
        path = 'index.html'
    file_path = os.path.join(settings.MUNIN_DIR, path)
    if not file_path.startswith(settings.MUNIN_DIR):
        # User tried to inject ".."
        raise Http404()
    if not os.path.exists(file_path):
        raise Http404()
    if not os.path.isfile(file_path):
        raise PermissionDenied()
    fsock = open(file_path, 'rb')
    try:
        content_type = MimeTypes().guess_type(file_path)[0]
    except Exception as e:
        logger.error('Unable to guess content type of file "%s": %s', file_path, e)
        content_type = None
    return HttpResponse(fsock, content_type=content_type)


@login_required
def munin_cgi(request, path):
    # Prepare args for CGI script
    full_path = request.get_full_path()
    splitted = path.split('/')
    if len(splitted) < 3 or '?' not in full_path:
        raise Http404()
    script = splitted[0]
    if script not in ('munin-cgi-html', 'munin-cgi-graph'):
        raise Http404()
    script = os.path.join(settings.MUNIN_SCRIPTS_DIR, script)
    path_info = '/' + '/'.join(splitted[1:])
    query_string = full_path.split('?')[1].strip('&')
    # Run CGI script
    # http://www.ietf.org/rfc/rfc3875
    p = subprocess.Popen([script], env=dict(LANG='C', PATH_INFO=path_info, QUERY_STRING=query_string, REQUEST_METHOD='GET'), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    out, err = p.communicate()
    if p.returncode != 0:
        msg = 'Munin CGI script returned code %s.\n%s' % (p.returncode, err)
        logger.error(msg)
        return HttpResponse(msg, content_type='text/plain')
    # Remove header
    if b'PNG' in out:
        index = out.index(b'PNG')
        lines = out[:index].count(b'\n')
        out = b'\n'.join(out.split(b'\n')[lines:])
        return HttpResponse(out, content_type='image/png')
    elif 'Status: 404 Not Found':
        raise Http404()
    else:
        msg = 'Munin CGI script returned an handled response.'
        logger.error(msg + '\n' + out[:200])
        return HttpResponse(msg, content_type='text/plain')


@login_required
def ark(request):
    # ARK server management
    tplt_args = dict()

    if request.method == 'POST':
        actions = ('restart', 'stop', 'dump', 'update', 'validate')
        if request.POST.get('action') in actions:
            action = request.POST['action']
        else:
            action = 'restart'
        cmd = ['sudo', '-SnH', os.path.join(homesite.__path__[0], 'scripts', 'ark_server.py'), action, request.user.username]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        out, err = p.communicate()
        out = str(out, 'utf-8').strip() if out else 'No stdout.'
        err = str(err, 'utf-8').strip() if err else 'No stderr.'
        msg_pattern = '%%s\nStdout:\n%s\nStderr:\n%s' % (out, err)
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
        ps_out += '\n' + str(err, 'utf-8')
    if not ps_out:
        ps_out = _('Server is not running.')
    else:
        ps_out = '>>> ' + cmd + '\n' + ps_out
    tplt_args['ps_out'] = ps_out

    # Get log content
    path = '/home/steam/ark/ark_server.log'
    log = _('Log file does not exists.')
    if os.path.isfile(path):
        with open(path, 'r') as fd:
            log = fd.read()
        if not log:
            log = _('Log file is empty.')
    tplt_args['log'] = log

    tplt_args['section'] = 'ark'
    return render(request, 'base/ark.html', tplt_args)
