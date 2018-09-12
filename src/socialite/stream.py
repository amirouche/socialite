from time import time
from uuid import UUID

import daiquiri
from mistune import Markdown
from aiohttp import web

from socialite import fdb
from socialite import sparky
from socialite.user import user_by_username


log = daiquiri.getLogger(__name__)


markdown = Markdown()


@fdb.transactional
async def expressions_for_user(tr, username):
    patterns = [
        ('actor', sparky.var('actor'), 'name', username),
        ('stream', sparky.var('expression'), 'html', sparky.var('html')),
        ('stream', sparky.var('expression'), 'actor', sparky.var('actor')),
        ('stream', sparky.var('expression'), 'modified-at', sparky.var('modified-at')),
    ]
    out = await sparky.where(tr, *patterns)
    out.sort(key=lambda x: x['modified-at'], reverse=True)
    out = out[:100]
    return out


async def expressions(request):
    username = request.match_info['username']
    log.debug("Stream for username='%s'", username)
    expressions = await expressions_for_user(request.app['db'], username)
    context = {
        "settings": request.app["settings"],
        "username": username,
        "expressions": expressions,
        "current_user": request.user,
    }
    return request.app.render("stream/user.jinja2", request, context)


@fdb.transactional
async def stream(tr, user):
    """Fetch latest expressions of things that ``user`` follows"""
    # fetch followee aka. what user follows
    patterns = [
        ('stream', sparky.var('following'), 'follower', user),
        ('stream', sparky.var('following'), 'followee', sparky.var('followee')),
        ('stream', sparky.var('expression'), 'html', sparky.var('html')),
        ('stream', sparky.var('expression'), 'user', sparky.var('followee')),
        ('stream', sparky.var('expression'), 'modified-at', sparky.var('modified-at')),
        ('actor', sparky.var('followee'), 'name', sparky.var('name')),
    ]
    out = await sparky.where(tr, *patterns)
    out.sort(key=lambda x: x['modified-at'], reverse=True)
    out = out[:100]
    return out


async def stream_get(request):
    expressions = await stream(request.app["db"], request.user['uid'])
    context = {"settings": request.app["settings"], "expressions": expressions}
    return request.app.render("stream/stream.jinja2", request, context)


@fdb.transactional
async def expression_insert(tr, user, expression, html):
    now = int(time())
    uid = sparky.random_uid(tr)
    tuples = [
        ('stream', uid, 'html', html),
        ('stream', uid, 'expression', expression),
        ('stream', uid, 'user', user),
        ('stream', uid, 'modified-at', now),
        ('stream', uid, 'created-at', now),
    ]
    await sparky.add(tr, *tuples)
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
