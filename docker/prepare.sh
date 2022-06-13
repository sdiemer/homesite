# Script to prepare docker environment
mkdir -p /opt/src/docker/data
ln -sfn /opt/src/docker/data /home/djdev/homesite-data

mkdir -p /opt/src/docker/data/static
ln -sfn /opt/src/homesite/static/homesite /opt/src/docker/data/static/
ln -sfn /opt/src/django_web_utils/file_browser/static/file_browser /opt/src/docker/data/static/
ln -sfn /opt/src/django_web_utils/monitoring/static/monitoring /opt/src/docker/data/static/
