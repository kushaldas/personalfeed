#!/usr/bin/bash
redis-server &
/source/webfeed/updatefeed &
python /source/webfeed/__init__.py
