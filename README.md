# Homesite

Simple web site for my home server.

## OS dependencies

* munin
* munin-node
* [libcgi-fast-perl]
* uwsgi
* uwsgi-plugin-python3

## Installation on Debian/Ubuntu

### First initialization

``` bash
mkdir -p /opt/homesite
cd /opt/homesite
git clone --recursive https://github.com/sdiemer/homesite.git repo
bash /opt/homesite/repo/deployment/setup.sh
```

### Update

``` bash
bash /opt/homesite/repo/deployment/setup.sh
```

### Superuser account creation

``` bash
TODO
```
