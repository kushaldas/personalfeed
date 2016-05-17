#!/usr/bin/bash
redis-server &
/source/webfeed/updatefeed &
python3 /source/webfeed/__init__.py
