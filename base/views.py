#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import subprocess
# Django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import http_date
from django.views.static import serve
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
    if not path:
        path = 'index.html'
    if path.endswith('static/style-new.css'):
        # patch CSS for black theme
        munin_css = os.path.join(settings.MUNIN_DIR, 'static/style-new.css')
        if os.path.exists(munin_css):
            local_css = os.path.join(settings.MEDIA_ROOT, 'munin-style-new-1.css')
            mtime = os.path.getmtime(munin_css)
            if not os.path.exists(local_css) or os.path.getmtime(local_css) != mtime:
                with open(munin_css, 'r') as fo:
                    content = fo.read()
                content += '''
html, body { background: #222; }
html, body, h1, h2, h3, p, span, div { color: #eee; }
a:link, a:visited, a:link:active, a:link:hover { color: #a2c1ff; }
#header, #footer { background: #111; }
#header, #footer, #content { border-color: #777; }
img, h1 .logo { filter: invert(100%); }
#legend th { border-color: #777; }
#legend .oddrow { background-color: #333333; }
#legend .oddrow td { border-color: #777; }
#legend .evenrow { background-color: #393939; }
#legend .evenrow td { border-color: #777; }
'''
                with open(local_css, 'w') as fo:
                    fo.write(content)
                os.utime(local_css, times=(mtime, mtime))
                logger.debug('Regenerated Munin style CSS.')
            response = FileResponse(open(local_css, 'rb'), content_type='text/css')
            response['Last-Modified'] = http_date(mtime)
            return response
    elif path == 'static/dynazoom.html':
        # add missing CSS in dynazoom.html
        path = os.path.join(settings.MUNIN_DIR, 'static/dynazoom.html')
        if not os.path.exists(path):
            raise Http404()
        with open(path, 'r') as fo:
            content = fo.read()
        content = content.replace('<head>', '<head>\n<link rel="stylesheet" href="style-new.css" type="text/css" />')
        response = HttpResponse(content, content_type='text/html')
        response['Last-Modified'] = http_date(os.path.getmtime(path))
        return response
    return serve(request, path, document_root=settings.MUNIN_DIR, show_indexes=False)


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
    cmd = ['sudo', '-E', '-u', 'www-data', '-g', 'www-data', script]
    path_info = '/' + '/'.join(splitted[1:])
    query_string = full_path.split('?')[1].strip('&')
    # Run CGI script
    # http://www.ietf.org/rfc/rfc3875
    p = subprocess.Popen(cmd, env=dict(LANG='C', PATH_INFO=path_info, QUERY_STRING=query_string, REQUEST_METHOD='GET'), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    out, err = p.communicate()
    if p.returncode != 0:
        msg = 'Munin CGI script returned code %s.\n%s' % (p.returncode, err)
        logger.error(msg)
        return HttpResponse(msg, content_type='text/plain', status=400)
    # Remove header
    if b'PNG' in out:
        index = out.index(b'PNG')
        lines = out[:index].count(b'\n')
        out = b'\n'.join(out.split(b'\n')[lines:])
        return HttpResponse(out, content_type='image/png')
    elif b'Status: 404 Not Found' in out:
        raise Http404()
    else:
        msg = 'Munin CGI script returned an unhandled response.'
        logger.error(msg + '\n' + out.decode('utf-8', 'ignore')[:200])
        return HttpResponse(msg, content_type='text/plain', status=400)
