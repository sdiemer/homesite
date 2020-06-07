#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Django
from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve


urlpatterns = [
    url(r'^favicon\.ico', RedirectView.as_view(permanent=True, url='/static/img/favicon.png'), name='favicon'),
    # Authentication
    url(r'^', include('django.contrib.auth.urls')),
    # I18N
    url(r'^i18n/', include('django.conf.urls.i18n'), name='i18n'),
    # Base app
    url(r'^', include('homesite.base.urls')),
    # media serving
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': settings.DEBUG}, name='media'),
]

# test pages
if settings.DEBUG:
    # 404 test page
    urlpatterns.append(url(r'^404/$', TemplateView.as_view(template_name='404.html'), name='test_404'))
    # 500 test page
    urlpatterns.append(url(r'^500/$', TemplateView.as_view(template_name='500.html'), name='test_500'))

if settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns.insert(0, url(r'^__debug__/', include(debug_toolbar.urls)))
