#!/usr/bin/env python
import redis
import hashlib
config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': None,
        }

rdb = redis.Redis(config['host'], config['port'], config['db'],\
                              config['password'])

url = raw_input("Enter the rss feed: ")
hash = hashlib.sha1(url).hexdigest()
rdb.hset('sites', url, hash)
print("Done")