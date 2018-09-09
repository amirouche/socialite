from time import time
from uuid import UUID

import daiquiri
from mistune import Markdown
from aiohttp import web

from socialite import collection
from socialite import fdb
from socialite.user import user_by_username
from socialite.user import user_by_uid


log = daiquiri.getLogger(__name__)


STREAM = collection.Collection.STREAM
USERS = collection.Collection.USERS
FOLLOWING = collection.Collection.FOLLOWING


markdown = Markdown()


@fdb.transactional
async def items_for_user(tr, user):
    # TODO: optimize using an index or something
    items = await collection.all(tr, STREAM)
    out = list()
    for item in items:
        if (item['emitter']['kind'] == 'user' and item['emitter']['uid'] == user['uid'].hex):
            out.append(item)
    out.sort(key=lambda x: x['modified_at'], reverse=True)
    return out


async def items(request):
    username = request.match_info['username']
    log.debug("Stream for username='%s'", username)
    try:
        user = await user_by_username(request.app['db'], username)
    except IndexError:
        raise web.HTTPNotFound()
    else:
        items = await items_for_user(request.app['db'], user)
        context = {
            "settings": request.app["settings"],
            "user": user,
            "items": items,
            "current_user": request.user,
        }
        return request.app.render("stream/items.jinja2", request, context)


@fdb.transactional
async def stream(tr, user):
    """Fetch latest items of things that ``user`` follows"""
    # fetch followee aka. what user follows
    query = {
        'follower_kind': 'user',
        'follower_uid': user['uid'].hex,
    }
    followees = await collection.query(tr, FOLLOWING, **query)
    log.critical(followees)
    followees = [(x['followee_kind'], x['followee_uid']) for x in followees]
    followees.append(('user', user["uid"].hex))
    # fetch items for the followees aka. filter
    items = await collection.all(tr, STREAM)
    out = []
    for item in items:
        key = (item['emitter']['kind'], item["emitter"]['uid'])
        if key in followees:
            out.append(item)
    out.sort(key=lambda x: x['modified_at'], reverse=True)
    out = out[:100]
    # fetch and embed users aka. join USER collection
    for item in out:
        uid = item['emitter']['uid']
        uid = UUID(hex=uid)
        user = await user_by_uid(tr, uid)
        item['user'] = user
    return out


async def stream_get(request):
    items = await stream(request.app["db"], request.user)
    context = {"settings": request.app["settings"], "items": items}
    return request.app.render("stream/stream.jinja2", request, context)


@fdb.transactional
async def expression_insert(tr, uid, expression, html):
    now = int(time())
    document = {
        'emitter': {
            'uid': uid.hex,
            'kind': 'user',
        },
        'source': {
            'kind': 'expression',
            'expression': expression,
        },
        'html': html,
        'created_at': now,
        'modified_at': now,
    }
    uid = await collection.insert(tr, STREAM, **document)
    return uid


async def stream_post(request):
    data = await request.post()
    expression = data['expression']
    log.debug('Post expression: %s', expression)
    # TODO: some security validation and sanitization like with bleach
    html = markdown(expression)
    await expression_insert(request.app['db'], request.user['uid'], expression, html)
    raise web.HTTPSeeOther(location="/stream/")


async def follow_get(request):
    username = request.match_info['username']
    log.debug("follow_get username=%r", username)
    user = await user_by_username(request.app["db"], username)
    context = {"settings": request.app["settings"], "user": user}
    return request.app.render("stream/follow.jinja2", request, context)


@fdb.transactional
async def follow(tr, user, username):
    uid = user.pop('uid')
    other = await user_by_username(tr, username)
    document = {
        'follower_uid': uid.hex,
        'follower_kind': 'user',
        'followee_uid': other['uid'].hex,
        'followee_kind': 'user',
    }
    await collection.insert(tr, FOLLOWING, **document)


async def follow_post(request):
    username = request.match_info['username']
    log.debug("follow_post username=%r", username)
    await follow(request.app["db"], request.user, username)
    raise web.HTTPSeeOther(location="/stream/")
