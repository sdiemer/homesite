from django.conf import settings
from django.urls import include, re_path

from homesite.base import views


urlpatterns = [
    re_path(r'^get_ip/$', views.get_ip, name='get_ip'),
    # File brwoser
    re_path(r'^public-ui/', include(('django_web_utils.file_browser.urls', 'fb-public'), namespace='fb-public'), {'namespace': 'fb-public'}),
    re_path(r'^public/(?P<path>.+)$', views.serve_path, {'root_dir': settings.FB_PUBLIC_ROOT, 'login_required': False}, name='public_serve'),  # Hosted by Nginx
    # Protected file brwoser
    re_path(r'^protected-ui/', include(('django_web_utils.file_browser.urls', 'fb-protected'), namespace='fb-protected'), {'namespace': 'fb-protected'}),
    re_path(r'^protected/(?P<path>.+)$', views.serve_path, {'root_dir': settings.FB_PROTECTED_ROOT, 'login_required': True}, name='protected_serve'),
    # Daemons monitoring
    re_path(r'^daemons/', include(('django_web_utils.monitoring.urls', 'monitoring'), namespace='monitoring')),
    # Munin
    re_path(r'^$', views.munin, name='munin'),
    re_path(r'^munin-src/(?P<path>.*)$', views.munin_file, name='munin_file'),
    re_path(r'^munin-cgi/(?P<path>.+)$', views.munin_cgi, name='munin_cgi'),
    # Server info
    re_path(r'^info/$', views.info, name='info'),
]
