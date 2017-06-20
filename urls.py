#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Django
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout_then_login
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve


admin.autodiscover()

urlpatterns = [
    url(r'^favicon.ico', RedirectView.as_view(permanent=True, url='/static/img/favicon.png'), name='favicon'),
    # I18N
    url(r'^i18n/', include('django.conf.urls.i18n'), name='i18n'),
    # login, logout
    url(r'^login/$', login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', logout_then_login, name='logout'),
    # Base app
    url(r'^', include('homesite.base.urls')),
    # django admin
    url(r'^django/', admin.site.urls),
    # media serving
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': settings.DEBUG}, name='media'),
    # Your app
    # url(r'^', include('homesite.yourapp.urls')),
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
