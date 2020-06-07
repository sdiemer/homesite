# Homesite

Simple web site for my home server.

## Dependencies

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
adduser --system --disabled-password --group homesite --shell /bin/bash
```

### Clone project

``` bash
cd /home/homesite
git clone https://github.com/sdiemer/homesite.git
chown -R homesite:homesite /home/homesite
```

### Superuser account creation

``` bash
python3 homesite/scripts/control.py createuser admin@example.com:test:superuser
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
