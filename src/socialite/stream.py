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

markdown = Markdown()


@fdb.transactional
async def items_for_user(tr, user):
    # TODO: optimize using an index or something
    items = await collection.query(tr, STREAM, user=user['uid'].hex)
    items.sort(key=lambda x: x['modified_at'], reverse=True)
    return items


async def items(request):
    username = request.match_info['username']
    log.debug("Stream for username='%s'", username)
    try:
        user = await user_by_username(request.app['db'], username)
    except IndexError:
        raise web.HTTPNotFound()
    else:
        items = await items_for_user(request.app['db'], user)
        log.debug('items is %r', items)
        context = {"settings": request.app["settings"], "user": user, "items": items}
        return request.app.render("stream/items.jinja2", request, context)


@fdb.transactional
async def timeline(tr, user):
    followee = user.get('followee', [])
    followee.append(user["uid"].hex)
    items = await collection.all(tr, STREAM)
    out = []
    for item in items:
        if item["user"] in followee:
            out.append(item)
    out.sort(key=lambda x: x['modified_at'], reverse=True)
    out = out[:100]
    # join users
    for item in out:
        uid = item['user']
        uid = UUID(hex=uid)
        user = await user_by_uid(tr, uid)
        item['user'] = user

    return out


async def timeline_get(request):
    items = await timeline(request.app["db"], request.user)
    context = {"settings": request.app["settings"], "items": items}
    return request.app.render("stream/stream.jinja2", request, context)


@fdb.transactional
async def expression_insert(tr, uid, expression, html):
    now = int(time())
    document = {
        'user': uid.hex,  # XXX: because msgpack doesn't have a disjoint type for bytes
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


async def timeline_post(request):
    data = await request.post()
    expression = data['expression']
    log.debug('Post expression: %s', expression)
    # TODO: some security validation and sanitization like with bleach
    html = markdown(expression)
    await expression_insert(request.app['db'], request.user['uid'], expression, html)
    raise web.HTTPSeeOther(location="/stream/")
