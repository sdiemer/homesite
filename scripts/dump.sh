#!/bin/bash
mysqldump -u homesite homesite --ignore-table=homesite.django_session > "/home/homesite/dbdumps/homesite_dev_$(date +%Y-%m-%d_%H-%M-%S).sql"
