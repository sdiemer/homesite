#!/bin/bash
if [[ $(id -u) != "0" ]]; then
    echo "This script must be run as root"
    exit 1
fi

set -e
set -x

# Create app user
if ! id -u homesite; then
	adduser --system --group --shell /usr/sbin/nologin --home /opt/homesite/data homesite
fi

# Clean temp files and update repository
cd /opt/homesite/repo
find . -name *.pyc -type f -delete
find . -name __pycache__ -type d -delete
git fetch --recurse-submodules --all
git reset --hard origin/main
git pull --recurse-submodules

# Check virtual env
if ! test -d /opt/homesite/venv; then
	python3 -m venv /opt/homesite/venv
fi
/opt/homesite/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel
/opt/homesite/venv/bin/pip install --no-cache-dir --editable '.'

# Main entry point
ln -sfn /opt/homesite/venv/bin/homesite-control /usr/local/bin/homesite-control

# Init settings file
mkdir -p /opt/homesite/data/private
if ! grep SECRET_KEY /opt/homesite/data/private/settings_override.py; then
	secret_key=$(tr -dc 'a-z0-9!@#$%^&*\-_=+(){}[]' < /dev/urandom | head -c50)
	echo "SECRET_KEY = '${secret_key}'" >> /opt/homesite/data/private/settings_override.py
	echo "Secret key generated."
fi
if ! grep SITE_DOMAIN /opt/homesite/data/private/settings_override.py; then
	echo "SITE_DOMAIN = 'homesite'" >> /opt/homesite/data/private/settings_override.py
	echo "Site domain added to settings."
fi

# Ensure files ownership and permissions
chown -R homesite: /opt/homesite/data
chown homesite:www-data /opt/homesite/data
chmod 700 /opt/homesite/data/private

# Nginx configuration
site_domain=$(grep SITE_DOMAIN /opt/homesite/data/private/settings_override.py | awk '{print $2}' FS='=' | tr -d "' \"")
sed -i "s/server_name vhost-domain;/server_name ${site_domain};/g" /opt/homesite/repo/deployment/nginx.conf
ln -sfn /opt/homesite/repo/deployment/nginx.conf /etc/nginx/sites-available/homesite.conf
ln -sfn ../sites-available/homesite.conf /etc/nginx/sites-enabled/homesite.conf
if ! test -f /etc/nginx/conf.d/ssl.conf; then
	echo 'ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;' > /etc/nginx/conf.d/ssl.conf
	echo 'ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;' >> /etc/nginx/conf.d/ssl.conf
fi
nginx -t
systemctl reload nginx

# Munin setup
if test -d /var/lib/munin; then
	touch /var/log/munin/munin-cgi-graph.log
	touch /var/log/munin/munin-cgi-html.log
	chmod 660 /var/log/munin/munin-cgi-*
	chown www-data:homesite /var/log/munin/munin-cgi-*
	mkdir -p /var/lib/munin/cgi-tmp/munin-cgi-graph
	chmod -R 770 /var/lib/munin/cgi-tmp/munin-cgi-graph
	chown -R www-data:homesite /var/lib/munin/cgi-tmp/munin-cgi-graph
fi

# Systemd service
ln -sfn /opt/homesite/repo/deployment/homesite.service /lib/systemd/system/homesite.service
systemctl enable homesite
systemctl restart homesite


echo -e "    \033[92m[ OK ]\033[0m"
exit 0
