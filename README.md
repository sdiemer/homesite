# Homesite

Simple web site for my home server.

## Dependencies

* python3-bleach
* python3-django
* python3-django-web-utils
* python3-pil
* munin
* munin-node
* [libcgi-fast-perl]
* uwsgi
* uwsgi-plugin-python3

## Installation on Debian/Ubuntu

### Add systel user to run the project

``` bash
adduser --disabled-password --shell /usr/sbin/nologin homesite
```

### Clone project

``` bash
cd /opt
git clone --recursive https://github.com/sdiemer/homesite.git
chown -R homesite: /opt/homesite
ln -s /opt/homesite/homesite/scripts/homesite.service /lib/systemd/system/
ln -s /opt/homesite/homesite/scripts/control.py /usr/local/bin/homesite-control
```

### Init project

``` bash
mkdir -p /home/homesite/homesite-data/private
secret_key=$(tr -dc 'a-z0-9!@#$%^&*\-_=+(){}[]' < /dev/urandom | head -c50)
echo "SECRET_KEY = '$secret_key'" >> "/home/homesite/homesite-data/private/settings_override.py"
chown -R homesite: /home/homesite
chmod 700 /home/homesite/homesite-data/private
runuser -u homesite -- python3 /opt/homesite/homesite/manage.py migrate
```

### Superuser account creation

``` bash
runuser -u homesite -- python3 /opt/homesite/homesite/manage.py createsuperuser --username admin
```

### Optional: Munin configuration to access to cgi generated files (graphs zoom)

``` bash
touch /var/log/munin/munin-cgi-graph.log
touch /var/log/munin/munin-cgi-html.log
chmod 660 /var/log/munin/munin-cgi-*
chown www-data:homesite /var/log/munin/munin-cgi-*
mkdir -p /var/lib/munin/cgi-tmp/munin-cgi-graph
chmod -R 770 /var/lib/munin/cgi-tmp/munin-cgi-graph
chown -R www-data:homesite /var/lib/munin/cgi-tmp/munin-cgi-graph
```
