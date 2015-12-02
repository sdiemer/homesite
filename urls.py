#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Django
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve


@login_required
def protected_serve(request, *args, **kwargs):
    return serve(request, *args, **kwargs)


admin.autodiscover()

urlpatterns = patterns(
    '',  # prefix
    url(r'^favicon.ico', RedirectView.as_view(permanent=True, url='/static/img/favicon.png'), name='favicon'),
    # media serving
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': settings.DEBUG}, name='media'),
    url(r'^get_ip/$', 'homesite.main.views.get_ip', name='get_ip'),

    # I18N
    url(r'^i18n/', include('django.conf.urls.i18n'), name='i18n'),

    # login, logout
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    # django admin
    url(r'^django/', include(admin.site.urls), name='admin_django'),

    # file brwoser
    url(r'^storage/public-ui/', include('django_web_utils.file_browser.urls', namespace='fb-public'), {'namespace': 'fb-public'}),
    url(r'^storage/public/(?P<path>.*)$', serve, {'document_root': settings.FB_PUBLIC_ROOT, 'show_indexes': settings.DEBUG}),
    # protected file brwoser
    url(r'^storage/private-ui/', include('django_web_utils.file_browser.urls', namespace='fb-private'), {'namespace': 'fb-private'}),
    url(r'^storage/private/(?P<path>.*)$', protected_serve, {'document_root': settings.FB_PRIVATE_ROOT, 'show_indexes': settings.DEBUG}),

    # ark server management
    url(r'^$', 'homesite.main.views.ark', name='ark'),

    # server info
    url(r'^info/$', 'homesite.main.views.info', name='info'),

    # munin
    url(r'^munin/$', 'homesite.main.views_munin.munin', name='munin'),
    url(r'^munin-src/(?P<path>.*)$', 'homesite.main.views_munin.munin_file', name='munin_file'),
    url(r'^munin-cgi/(?P<path>.+)$', 'homesite.main.views_munin.munin_cgi', name='munin_cgi'),
)

# test pages
if settings.DEBUG:
    urlpatterns += patterns(
        '',
        # 404 test page
        url(r'^404/$', TemplateView.as_view(template_name='404.html'), name='test_404'),
        # 500 test page
        url(r'^500/$', TemplateView.as_view(template_name='500.html'), name='test_500'),
    )
