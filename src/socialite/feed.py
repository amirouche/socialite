from time import time

import async_timeout
import daiquiri
import trafaret as t
from aiohttp import web
from defusedxml.lxml import fromstring as bytes2xml

from socialite.base import SocialiteException
from socialite import fdb
from socialite import sparky


log = daiquiri.getLogger(__name__)


TIMEOUT_FEED_FETCH = 3


class FeedException(SocialiteException):
    """Base error for the feed module"""
    pass


class FeedNotFound(FeedException):
    """Server error"""
    pass


class UnknownFeedFormat(FeedException):
    """Try to parse a feed using the wrong format"""
    pass


async def fetch(session, url):
    async with async_timeout.timeout(TIMEOUT_FEED_FETCH):
        async with session.get(url) as response:
            if response.status != 200:
                log.error("feed not found at url=%r response=%r", response)
                raise FeedNotFound((url, response.status))
            else:
                out = await response.read()
                return out


def extract(raw, source):
    xml = bytes2xml(raw)
    root = xml.tag
    if root == 'rss':
        out = {
            'title': xml.xpath('/rss/channel/title/text()')[0],
            'entries': [],
        }
        for item in xml.xpath('/rss/channel/item'):
            entry = {
                'title': item.xpath('./title/text()')[0].strip(),
                'link': item.xpath('./link/text()')[0].strip(),
            }
            out['entries'].append(entry)
        return out
    elif root == '{http://www.w3.org/2005/Atom}feed':
        namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
        title = xml.xpath('/atom:feed/atom:title/text()', namespaces=namespaces)[0].strip()
        out = {
            'source': source,
            'title': title,
            'entries': [],
        }
        for item in xml.xpath('/atom:feed/atom:entry', namespaces=namespaces):
            # try to get link
            try:
                link = item.xpath('./atom:link/text()', namespaces=namespaces)[0]
            except IndexError:
                link = False
            else:
                link = link.strip()
            if not link:
                link = item.xpath('./atom:link/@href', namespaces=namespaces)[0]
            # try to get title
            title = item.xpath('./atom:title/text()', namespaces=namespaces)[0]
            title = title.strip()
            entry = {
                'title': title,
                'link': link,
            }
            out['entries'].append(entry)
        return out
    else:
        raise UnknownFeedFormat(source, root)


async def parse(session, url):
    try:
        raw = await fetch(session, url)
        return extract(raw, url)
    except Exception as exc:
        raise FeedException('Failed to parse') from exc


@fdb.transactional
async def add(tr, feed):
    # TODO: check that the feed doesn't already exists
    uid = feed['uid'] = await sparky.random_uid(tr)
    tuples = [
        ('actor', uid, 'name', feed['title']),
        ('actor', uid, 'is a', 'feed'),
    ]
    for entry in feed['entries']:
        uid = await sparky.random_uid(tr)
        html = '<div><p><a href="{}">{}</a></p></div>'
        html = html.format(entry['link'], entry['title'])
        now = int(time())
        tuples.extend([
            ('stream', uid, 'html', html),
            ('stream', uid, 'expression', entry['title']),
            ('stream', uid, 'actor', feed['uid']),
            ('stream', uid, 'modified-at', now),
            ('stream', uid, 'created-at', now),
        ])

    await sparky.add(tr, *tuples)

    return feed['title']


async def add_post(request):
    data = await request.post()
    url = data['url']
    try:
        url = t.URL(url)
    except t.DataError:
        raise web.HTTPBadRequest()
    feed = await parse(request.app['session'], url)
    name = await add(request.app['db'], feed)
    log.debug('added stream name=%r', name)
    location = '/stream/{}'.format(name)
    raise web.HTTPSeeOther(location=location)
