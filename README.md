Homesite
========

Simple web site for my home server.

Dependencies:

* python3-django
* python3-django-web-utils
* python3-pil
* munin
* munin-node
* libcgi-fast-perl
* uwsgi
* uwsgi-plugin-python3

Munin configuration to access to cgi generated files :

touch /var/log/munin/munin-cgi-graph.log
touch /var/log/munin/munin-cgi-html.log
chmod 660 /var/log/munin/munin-cgi-*
chown www-data:homesite /var/log/munin/munin-cgi-*
mkdir -p /var/lib/munin/cgi-tmp/munin-cgi-graph
chmod -R 770 /var/lib/munin/cgi-tmp/munin-cgi-graph
chown -R www-data:homesite /var/lib/munin/cgi-tmp/munin-cgi-graph
