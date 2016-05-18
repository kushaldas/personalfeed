import flask
import json
import logging
from pprint import pprint
import os
import hashlib
from flask import Flask, request
from pyfeed import startpoint

log = logging.getLogger()
log.level = logging.DEBUG
#fh = logging.FileHandler('/tmp/web.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
#fh.setFormatter(formatter)
#log.addHandler(fh)


RDB = {'sites':{}, 'groups':{}}

DBNAME = None

class SiteDetails(object):

    def __init__(self, feed, hashvalue, unread=0, current=False):
        self.url = ""
        self.feed = feed
        self.hashvalue = hashvalue
        self.unread = unread
        self.current = current
        self.items = []
        self.item_urls = {}

class GroupDetails(object):

    def __init__(self, name):
        self.name = name
        self.items = []


def get_all_site_details(name):
    """
    Creates the all sites details for the navbar
    :return: A list of sites.
    """
    global RDB
    result = []
    groups = RDB['groups']
    for g, gsites in groups.items():
        ir = GroupDetails(g)
        for k in gsites:
            data = RDB['sites'].get(k)
            if data.hashvalue == name.strip():
                data.current = True
            ir.items.append(data)
        result.append(ir)
    return result

app = Flask(__name__)
@app.route('/')
def hello_world():
    global RDB
    sites = RDB['sites']
    sites = {v.feed:k for k,v in sites.items()}
    return flask.render_template('home.html', links=sites)

@app.route('/read/<name>/')
def read_a_site(name):
    global RDB
    allsites = get_all_site_details(name)
    pprint(allsites)
    site = RDB['sites'][name]
    site.unread = 0
    RDB['sites'][name] = site
    posts = site.items
    return flask.render_template('posts.html', posts=posts, allsites=allsites)

@app.route('/addsites/<group>/',methods=['GET', 'POST'])
def addsite(group):
    global RDB
    if request.method == 'POST':
        url = request.form['url']
        url = url.strip()
        grp = request.form['group']
        grp = grp.strip()
        hash = hashlib.sha1(url.encode()).hexdigest()
        site = SiteDetails(url, hash)
        RDB['sites'][hash] = site
        RDB['groups'].setdefault(grp, []).append(hash)
        return flask.render_template('addsites.html', group=group)
    else:
        return flask.render_template('addsites.html', group=group)

@app.route('/update/')
def update_sites():
    global RDB
    RDB = startpoint(RDB)
    return flask.redirect(flask.url_for('hello_world'))



if __name__ == '__main__':
    if os.path.exists('/output/'):
        DBNAME = '/output/site.db'
    else:
        DBNAME = '/tmp/site.db'
    app.run(host='0.0.0.0', debug=True)
