#pragma pylint: disable=broad-except
from datetime import datetime
import time
import re
import logging

import pprint
import requests
import feedparser
import urllib3

from heap import db
from heap.models import Source, Item

urllib3.disable_warnings()
pp = pprint.PrettyPrinter(indent=4)
logger = logging.getLogger(__name__)

#pylint: disable=line-too-long
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

def update_feeds():
    #wrapper around update_feed function to loop through all feeds
    sources = Source.query.all()
    item_count = len(Item.query.all())
    for source in sources:
        update_feed(source)
    print("Updated {} items".format(len(Item.query.all()) - item_count))

def resolve_url(url):
    found = False
    x_frame_options = False
    tries = 0
    while not found:
        tries = tries + 1
        try:
            res = requests.get(url, headers={
                'User-Agent': DEFAULT_USER_AGENT})
            if url == res.url:
                found = True
            else:
                logger.info("redirected from %s to %s", url, res.url)
                url = res.url
                x_frame_options = 'x-frame-options' in res.headers.keys()
        except Exception as e:
            logger.error(e)
            found = True
        if tries > 5:
            break
    return url, x_frame_options

def resolve_urls():
    # get the final urls after all the redirects
    items = Item.query.filter(Item.read.is_(False), Item.url.like("http://theawesomer%")).all()
    for item in items:
        url, x_frame_options = resolve_url(item.url)
        item.url = url
        item.x_frame_options = x_frame_options
    db.session.commit()

#pylint: disable=too-many-branches
def update_feed(source):
    # get the new items from the feed and add them to the db
    url = source.url
    if source.refresh_token:
        # refresh_token implies that the source is a reddit source
        access_token = get_access_token(source.refresh_token)
        hdr = {'Authorization': 'bearer %s' % access_token, 'User-Agent': 'Heap by /u/fizzy123'}
        res = requests.get(url, headers=hdr)
        while res.status_code == 503:
            time.sleep(60)
            res = requests.get(url, headers=hdr)
        data = res.json()['data']
        source.name = 'Reddit Feed'
        if source.updated:
            # checks whether or not items have been pulled from this source before or not
            new_entries = []
            for entry in data['children']:
                if not Item.query.filter(Item.source_id == Source.id) \
                                 .filter(Item.url == "https://www.reddit.com{}".format(entry['data']['permalink'])) \
                                 .first():
                    new_entries.append(entry)
        else:
            new_entries = data['children']
        for entry in new_entries:
            item = Item(source_id=source.id, user_id=source.user_id, url='https://www.reddit.com' + entry['data']['permalink'], x_frame_options=True)
            db.session.add(item)
    else:
        # pull rss feed
        feed = feedparser.parse(url)
        if (not source.name or not re.search(r"Hacker News: ", source.name)) and hasattr(feed.feed, 'title'):
            # Want to include score in hacker news rss feed,
            # so we don't take the title from the feed object
            source.name = feed.feed.title
        elif not hasattr(feed.feed, 'title'):
            # if feed object has no title, just name it after the url
            source.name = url
        if source.updated:
            # checks whether or not items have been pulled from this source before or not
            new_entries = [entry for entry in feed.entries if (hasattr(entry, 'published_parsed')) and (datetime(*(entry.published_parsed[0:6])) > source.updated)]
        else:
            new_entries = feed.entries
        for entry in new_entries:
            url, x_frame_options = resolve_url(entry.link)
            item = Item.query.filter(Item.url == url, Item.source == source).first()
            if not item:
                item = Item(source_id=source.id, user_id=source.user_id, url=url, x_frame_options=x_frame_options)
                db.session.add(item)
    db.session.commit()

def get_access_token(refresh_token):
    url = 'https://www.reddit.com/api/v1/access_token'
    username = 's03SUqQUXI4Txw'
    password = 'QsWUsTMAW4e0BH2c90NJ7zH3Kz8'
    client_auth = requests.auth.HTTPBasicAuth(username, password)
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    hdr = {
        'User-Agent': 'web:heap:v1.0 (by /u/fizzy123)'
    }
    response = requests.post(url,
                             auth=client_auth,
                             data=data,
                             headers=hdr)
    while response.status_code == 503:
        time.sleep(60)
        response = requests.post(url,
                                 auth=client_auth,
                                 data=data,
                                 headers=hdr)
    access_token = response.json()['access_token']
    return access_token
