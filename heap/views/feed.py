import logging
import requests
from sqlalchemy import func
from flask import Blueprint, redirect, jsonify, session, url_for, request

from heap import db
from heap.models import User, Item, Source
from heap.functions import update_feed
from .decorators import login_required

logger = logging.getLogger(__name__)

feed_blueprint = Blueprint('feed', __name__)

@feed_blueprint.route('/redirect/', methods=['GET'])
@login_required
def redirect_view(newtab=True):
    iframe = False
    if newtab:
        item = Item.query.join(Source) \
                         .join(User) \
                         .filter(User.id == session['user'],
                                 Item.read.is_(False),
                                 Item.x_frame_options.is_(False)) \
                         .order_by(func.random()) \
                         .first()
        if item:
            iframe = True
    if not iframe:
        item = Item.query.join(Source) \
                         .join(User) \
                         .filter(User.id == session['user'],
                                 Item.read.is_(False)) \
                         .order_by(func.random()) \
                         .first()

    if item:
        return jsonify({'url': item.url, 'iframe': iframe})
    return jsonify({'url': url_for('ui.feeds_view')})

@feed_blueprint.route('/add_source/', methods=['POST'])
@login_required
def add_source_view():
    #not being escaped cause we're just adding a source
    url = request.form.get('url')
    if request.form.get('refresh_token'):
        source = Source.query.join(User) \
                             .filter(User.id == session['user'],
                                     Source.url == url,
                                     Source.refresh_token == request.form.get('refresh_token')) \
                             .first()
    else:
        source = Source.query.join(User) \
                             .filter(User.id == session['user'],
                                     Source.url == url) \
                             .first()

    update_feed(source)
    if request.form.get('score'):
        source.name = 'Hacker News: Score ' + request.form.get('score')
    db.session.commit()
    return jsonify({'success': True, 'source': source.dictify()})

@feed_blueprint.route('/add_hn_source/', methods=['POST'])
@login_required
def add_hn_source_view():
    request.form['url'] = 'http://hnapp.com/rss?q=type%3Astory%20score>' + request.form.get('score')
    return add_source_view()

@feed_blueprint.route('/delete_source/', methods=['POST'])
@login_required
def delete_source_view():
    source = Source.query.get(request.form.get('id'))
    db.session.delete(source)
    db.session.commit()
    return jsonify({'success': True})

@feed_blueprint.route('/check_url/', methods=['POST'])
@login_required
def check_url_view():
    item = Item.query.join(Source) \
                     .join(User) \
                     .filter(Item.url.contains(parse_url(request.form.get('url'))),
                             Item.read.is_(False),
                             User.id == session['user']) \
                     .first()
    if item:
        return jsonify({'url': item.url})
    return jsonify({})

@feed_blueprint.route('/action/', methods=['POST'])
@login_required
def action_view():
    item = Item.query.join(Source) \
                     .join(User) \
                     .filter(Item.url.contains(parse_url(request.form.get('url'))),
                             Item.read.is_(False),
                             User.id == session['user']) \
                     .first()
    if item:
        return mark_read_view(item)
    return add_item_view()

@feed_blueprint.route('/mark_read/', methods=['POST'])
@login_required
def mark_read_view(item=None):
    if not item:
        item = item.query.join(User) \
                         .filter(Item.url.contains(parse_url(request.form.get('url'))),
                                 Item.read.is_(False),
                                 User.id == session['user']) \
                         .first()
    item.read = True
    db.session.commit()
    return redirect_view(False)

@feed_blueprint.route('/add_item/', methods=['POST'])
@login_required
def add_item_view():
    #Not being parsed cause not being used in search
    url = request.utils.unquote(request.form.get('url')).decode("utf8")
    item = Item(url=url)
    db.session.add(item)
    db.session.commit()
    return jsonify({'success': True})

@feed_blueprint.route('/redditd/', methods=['GET', 'POST'])
@login_required
def redditd_view():
    if request.args.get('error') or request.args.get('state') != request.cookies.get('reddit-key'):
        return redirect(url_for('ui.feeds_view'))
    username = 's03SUqQUXI4Txw'
    password = 'QsWUsTMAW4e0BH2c90NJ7zH3Kz8'
    client_auth = request.auth.HTTPBasicAuth(username, password)

    redirect_url = 'http://heap.nobr.me/feed/redditd/'
    post_data = {
        'grant_type': 'authorization_code',
        'code': request.args.get('code'),
        'redirect_uri': redirect_url
    }

    hdr = {
        'User-Agent': 'web:heap:v1.0 (by /u/fizzy123)'
    }
    url = 'https://www.reddit.com/api/v1/access_token'
    response = requests.post(url,
                             auth=client_auth,
                             data=post_data,
                             headers=hdr)
    res_dict = response.json()

    if 'error' in res_dict:
        return redirect(url_for('ui.feeds_view'))

    request.form['refresh_token'] = res_dict['refresh_token']
    request.form['url'] = 'https://oauth.reddit.com/hot.rss?sort=hot'
    add_source_view()

    return redirect(url_for('ui.feeds_view') + '?message=reddit_add')

def parse_url(url):
    url = bytes(url, 'utf-8').decode('utf-8', 'ignore')
    if 'www.bbc' in url:
        url = '/'.join(url.split('/')[3:])
    return url.split('#')[0].split('?')[0]
