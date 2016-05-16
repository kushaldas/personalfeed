import flask
import json
import logging
import redis
import dbm
from pprint import pprint
import hashlib
from flask import Flask, request

log = logging.getLogger()
log.level = logging.DEBUG
#fh = logging.FileHandler('/tmp/web.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
#fh.setFormatter(formatter)
#log.addHandler(fh)

config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': None,
        }

rdb = redis.Redis(config['host'], config['port'], config['db'],\
                              config['password'])

class SiteDetails(object):

    def __init__(self, url, value, unread, current=False):
        self.url = url
        self.value = value
        self.unread = unread
        self.current = current

class GroupDetails(object):

    def __init__(self, name):
        self.name = name
        self.items = []


def get_all_site_details(name):
    """
    Creates the all sites details for the navbar
    :return: A list of sites.
    """
    result = []
    sites = rdb.hgetall('sites')
    groups = rdb.keys("group:*")
    for g in groups:
        ir = GroupDetails(g.split(':')[1])
        gsites = rdb.lrange(g, 0, -1)
        for k in gsites:
            v = sites[k]
            unread = rdb.hget('pt:{0}'.format(v), 'unread')
            k = '/'.join(k.split('/')[:3])
            data = SiteDetails(k, v, unread)
            if v == name.strip():
                data.current = True
            ir.items.append(data)
        result.append(ir)
    return result

app = Flask(__name__)
@app.route('/')
def hello_world():
    sites = rdb.hgetall('sites')
    return flask.render_template('home.html', links=sites)

@app.route('/read/<name>/')
def read_a_site(name):
    allsites = get_all_site_details(name)
    fullposts = "fullposts:{0}".format(name)
    pturl = "pt:{0}".format(name)
    rdb.hset(pturl, 'unread', 0)
    posts = rdb.lrange(fullposts, 0, -1)
    posts = [json.loads(p) for p in posts]
    return flask.render_template('posts.html', posts=posts, allsites=allsites)

@app.route('/addsites/<group>/',methods=['GET', 'POST'])
def addsite(group):
    if request.method == 'POST':
        url = request.form['url']
        url = url.strip()
        grp = request.form['group']
        grp = grp.strip()
        hash = hashlib.sha1(url).hexdigest()
        rdb.hset('sites', url, hash)
        rdb.rpush('group:{0}'.format(grp), url)
        # Now let us save the data in dbm
        db = dbm.open('/output/site.db', 'c')
        db[url] = grp
        db.close()
        return flask.render_template('addsites.html', group=group)
    else:
        return flask.render_template('addsites.html', group=group)

@app.route('/update/')
def update_sites():
    rdb.lpush('updatejob', "hello")
    sites = rdb.hgetall('sites')
    return flask.render_template('home.html', links=sites)



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
