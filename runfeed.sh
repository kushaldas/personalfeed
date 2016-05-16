#!/usr/bin/bash
redis-server &
webfeed/updatefeed &
python webfeed/__init__.py
