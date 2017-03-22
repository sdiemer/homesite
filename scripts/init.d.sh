#!/bin/bash

### BEGIN INIT INFO
# Provides:          homesite
# Required-Start:    $local_fs $network $syslog
# Required-Stop:     $local_fs $network $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: homesite
# Description:       homesite management script
### END INIT INFO

# This script should be located in /etc/init.d/homesite
#   ln -s /home/homesite/homesite/scripts/init.d.sh /etc/init.d/homesite
# To make this script start at boot:
#   update-rc.d homesite defaults 96 00
# To remove it use:
#   update-rc.d -f homesite remove

if [[ $# < 1 ]]; then
    echo "Not enough arguments."
    exit 1
fi

/bin/su homesite -c "python3 /home/homesite/homesite/scripts/control.py $1"
exit $?
