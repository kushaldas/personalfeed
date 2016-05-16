import redis
import json
import feedparser

config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': None,
        }

rdb = redis.Redis(config['host'], config['port'], config['db'],\
                              config['password'])

def missing_link(key, link):
    """

    :param key: pt:URL a hash to find the current post URLS
    :param link: the post URL we are looking
    :return: True if it is missing, otherwise returns False
    """
    res = rdb.hget(key, link)
    if not res:
        return True
    else:
        return False


def startpoint():
    # first find all sites from the redis

    sites = rdb.hkeys('sites')
    for site in sites:
        val = rdb.hget('sites', site)
        fullposts = 'fullposts:{0}'.format(val)
        pturl = 'pt:{0}'.format(val)
        p = feedparser.parse(site)
        posts = p.entries
        unread = rdb.hget(pturl, 'unread')
        if not unread:
            unread = 0
        else:
            unread = int(unread)
        for p in posts[::-1]:
            # First check if it is already in list.
            link = p['link']
            if missing_link(pturl, link):
                rdb.hset(pturl, link, True)
                newd = {}
                for k in ['summary','title','link','author','published']:
                    newd[k] = p[k]
                if 'content' in p:
                    newd['content'] = p['content']
                else:
                    newd['content'] = p['summary']
                rdb.lpush(fullposts, json.dumps(newd))
                unread += 1
        # Now all posts update, let us strip the list
        rdb.ltrim(fullposts, 0, 20)
        rdb.hset(pturl, 'unread', unread)