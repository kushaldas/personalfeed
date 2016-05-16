import flask
import json
import logging
import redis
from pprint import pprint
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


app = Flask(__name__)
@app.route('/')
def hello_world():
    sites = rdb.hgetall('sites')
    return flask.render_template('home.html', links=sites)

@app.route('/read/<name>/')
def read_a_site(name):
    fullposts = "fullposts:{0}".format(name)
    pturl = "pt:{0}".format(name)
    rdb.hset(pturl, 'unread', 0)
    posts = rdb.lrange(fullposts, 0, -1)
    posts = [json.loads(p) for p in posts]
    return flask.render_template('posts.html', posts=posts)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
