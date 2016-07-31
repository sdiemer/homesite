#!/bin/bash

### BEGIN INIT INFO
# Provides:          homesite
# Required-Start:    $local_fs $network
# Required-Stop:     $local_fs $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts the homesite web platform
# Description:       starts homesite using uwsgi
### END INIT INFO

# This script should be located in /etc/init.d/homesite
#   ln -s uwsgi.sh /etc/init.d/homesite
# To make this script start at boot:
#   update-rc.d homesite defaults 96 00
# To remove it use:
#   update-rc.d -f homesite remove

PROJ_NAME="homesite"
PROJ_USER="homesite"
PROJ_DIR="/home/$PROJ_USER/homesite"
WSGI_INI="$PROJ_DIR/scripts/uwsgi.ini"
TEMP_DIR="$PROJ_DIR/temp"
PID_FILE="$TEMP_DIR/uwsgi.pid"

# check arg
if [[ $1 != "stop" && $1 != "start" && $1 != "restart" ]]; then
    echo "Usage: $0 start|stop|restart"
    exit 1
fi

cd $PROJ_DIR

# stop
if [[ $1 = "stop" || $1 = "start" || $1 = "restart" ]]; then
    echo "Stopping $PROJ_NAME ... "
    killed=false
    if [ -f $PID_FILE ]; then
        PID=$(cat -- $PID_FILE)
        if kill -9 $PID; then
            killed=true
        fi
        rm -f -- $PID_FILE
    fi
    if [[ !killed ]]; then
        pkill -9 -f -- "uwsgi --ini $WSGI_INI"
    fi
    echo -e "    \033[92m[ OK ]\033[0m"
fi

# start
if [[ $1 = "start" || $1 = "restart" ]]; then
    echo "Starting $PROJ_NAME ... "
    CMD_LINE="/bin/bash -c"
    if [[ $(whoami) != $PROJ_USER ]]; then
        CMD_LINE="sudo su $PROJ_USER -c"
    fi
    mkdir -p "$TEMP_DIR"
    unset UWSGI_ORIGINAL_PROC_NAME
    unset UWSGI_RELOADS
    $CMD_LINE "uwsgi --ini $WSGI_INI"
    if [ $? ]; then
        echo -e "    \033[92m[ OK ]\033[0m"
    else
        echo -e "    \033[91m[ FAILED ]\033[0m"
    fi
fi

cd - > /dev/null
exit 0
