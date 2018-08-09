#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Django
from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.static import serve
# homesite
from homesite.base import views


@login_required
def protected_serve(request, *args, **kwargs):
    return serve(request, *args, **kwargs)


urlpatterns = [
    url(r'^get_ip/$', views.get_ip, name='get_ip'),
    # file brwoser
    url(r'^storage/public-ui/', include(('django_web_utils.file_browser.urls', 'fb-public'), namespace='fb-public'), {'namespace': 'fb-public'}),
    url(r'^storage/public/(?P<path>.*)$', serve, {'document_root': settings.FB_PUBLIC_ROOT, 'show_indexes': settings.DEBUG}),
    # protected file brwoser
    url(r'^storage/private-ui/', include(('django_web_utils.file_browser.urls', 'fb-private'), namespace='fb-private'), {'namespace': 'fb-private'}),
    url(r'^storage/private/(?P<path>.*)$', protected_serve, {'document_root': settings.FB_PRIVATE_ROOT, 'show_indexes': settings.DEBUG}),
    # Daemons monitoring
    url(r'^daemons/', include('django_web_utils.monitoring.urls')),
    # ark server management
    url(r'^$', views.ark, name='ark'),
    # server info
    url(r'^info/$', views.info, name='info'),
    # munin
    url(r'^munin/$', views.munin, name='munin'),
    url(r'^munin-src/(?P<path>.*)$', views.munin_file, name='munin_file'),
    url(r'^munin-cgi/(?P<path>.+)$', views.munin_cgi, name='munin_cgi'),
]
