from bs4 import BeautifulSoup
import json
import feedparser
import sys
from pprint import pprint

# http://blog.yjl.im/2013/12/workaround-of-libxml2-unsupported.html
feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')




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

def startpoint(RDB):
    # first find all sites from the redis


    for key, site in RDB['sites'].items():
        p = feedparser.parse(site.feed)
        # Save the link to the site so that we can replace
        # the links where it is required
        if 'feed' in p and 'link' in p['feed']:
            url = p['feed']['link']
            if url.endswith('/'):
                url = url[:-1]
            site.url = url
        posts = p.entries
        for p in posts:
            # First check if it is already in list.
            link = p['link']
            if link not in site.item_urls:
                site.item_urls[link] = True
                newd = {}
                for k in ['summary','title','link','author','published']:
                    newd[k] = p[k]
                if 'content' in p:
                    newd['content'] = p['content']
                else:
                    newd['content'] = p['summary']
                # Now clean it up
                newd['content'] = recreate_links(newd['content'], url)
                site.items.append(newd)
                site.unread += 1
        # Now all posts update, let us strip the list
        RDB[key] = site
    return RDB