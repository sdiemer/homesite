#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf import settings
from django.urls import include, re_path
from django.contrib.auth.decorators import login_required
from django.views.static import serve

from homesite.base import views


@login_required
def protected_serve(request, *args, **kwargs):
    return serve(request, *args, **kwargs)


urlpatterns = [
    re_path(r'^get_ip/$', views.get_ip, name='get_ip'),
    # File brwoser
    re_path(r'^storage/public-ui/', include(('django_web_utils.file_browser.urls', 'fb-public'), namespace='fb-public'), {'namespace': 'fb-public'}),
    re_path(r'^storage/public/(?P<path>.*)$', serve, {'document_root': settings.FB_PUBLIC_ROOT, 'show_indexes': settings.DEBUG}),
    # Protected file brwoser
    re_path(r'^storage/protected-ui/', include(('django_web_utils.file_browser.urls', 'fb-protected'), namespace='fb-protected'), {'namespace': 'fb-protected'}),
    re_path(r'^storage/protected/(?P<path>.*)$', protected_serve, {'document_root': settings.FB_PROTECTED_ROOT, 'show_indexes': settings.DEBUG}),
    # Daemons monitoring
    re_path(r'^daemons/', include(('django_web_utils.monitoring.urls', 'monitoring'), namespace='monitoring')),
    # Munin
    re_path(r'^$', views.munin, name='munin'),
    re_path(r'^munin-src/(?P<path>.*)$', views.munin_file, name='munin_file'),
    re_path(r'^munin-cgi/(?P<path>.+)$', views.munin_cgi, name='munin_cgi'),
    # Server info
    re_path(r'^info/$', views.info, name='info'),
]
