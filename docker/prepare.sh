# Script to prepare docker environment
mkdir -p /opt/src/docker/data
ln -sfn /opt/src/docker/data /home/djdev/homesite-data

mkdir -p /opt/src/docker/data/static
ln -sfn /opt/src/homesite/static/homesite /opt/src/docker/data/static/
ln -sfn /opt/src/django_web_utils/file_browser/static/file_browser /opt/src/docker/data/static/
ln -sfn /opt/src/django_web_utils/monitoring/static/monitoring /opt/src/docker/data/static/

mkdir -p /opt/src/docker/data/private
if [ ! -f /opt/src/docker/data/private/settings_override.py ]; then
	echo '# Local settings
DEBUG = True
DEBUG_TOOLBAR = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
' > /opt/src/docker/data/private/settings_override.py
fi
