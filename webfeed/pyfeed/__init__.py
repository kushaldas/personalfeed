from bs4 import BeautifulSoup
import redis
import json
import feedparser
import sys

# http://blog.yjl.im/2013/12/workaround-of-libxml2-unsupported.html
feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')

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

def safe_strings(s):
    if type(s) == bytes:
        return s.decode()
    return s

def recreate_links(html_doc, url):
    "Clean up the html for right urls"
    if type(html_doc) == list:
        html_doc = html_doc[0]['value']
    res = []

    soup = BeautifulSoup(html_doc, 'html.parser')
    for link in soup.find_all('a'):
        text = link.get('href')
        if text.startswith('/'):
            res.append((text, "{0}{1}".format(url, text)))
    for link in soup.find_all('img'):
        text = link.get('src')
        if text.startswith('/'):
            res.append((text, "{0}{1}".format(url, text)))
    for k,v in res:
        html_doc = html_doc.replace(k, v)
    return html_doc

def startpoint():
    # first find all sites from the redis

    sites = rdb.hkeys('sites')
    for site in sites:
        site = site.decode()
        val = rdb.hget('sites', site)
        val = val.decode()
        fullposts = 'fullposts:{0}'.format(val)
        pturl = 'pt:{0}'.format(val)
        p = feedparser.parse(site)
        # Save the link to the site so that we can replace
        # the links where it is required
        if 'feed' in p and 'link' in p['feed']:
            url = p['feed']['link']
            if url.endswith('/'):
                url = url[:-1]
            rdb.hset(pturl, 'link', url)
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
                    newd[k] = safe_strings(p[k])
                if 'content' in p:
                    newd['content'] = safe_strings(p['content'])
                else:
                    newd['content'] = safe_strings(p['summary'])
                # Now clean it up
                newd['content'] = recreate_links(newd['content'], url)
                rdb.lpush(fullposts, json.dumps(newd))
                unread += 1
        # Now all posts update, let us strip the list
        rdb.ltrim(fullposts, 0, 20)
        rdb.hset(pturl, 'unread', unread)
