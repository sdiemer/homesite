#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mimetypes import MimeTypes
import logging
import os
import subprocess
# Django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import render

logger = logging.getLogger('homesite.main.views_munin')


@login_required
def munin(request):
    munin_url = reverse('munin_file', args=[settings.MUNIN_BASE])
    return render(request, 'munin.html', {
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
