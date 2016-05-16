#!/usr/bin/bash
redis-server &
python webfeed/__init__.py
