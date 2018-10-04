from time import time

import daiquiri
import found
from bleach import clean
from mistune import Markdown
from aiohttp import web


log = daiquiri.getLogger(__name__)


markdown = Markdown()


@found.transactional
async def expressions_for_user(tr, sparky, username):
    patterns = (
        (sparky.var("actor"), "name", username),
        (sparky.var("expression"), "actor", sparky.var("actor")),
        (sparky.var("expression"), "html", sparky.var("html")),
        (sparky.var("expression"), "modified-at", sparky.var("modified-at")),
    )
    out = await sparky.where(tr, *patterns)
    out.sort(key=lambda x: x["modified-at"], reverse=True)
    out = out[:100]
    return out


async def expressions(request):
    username = request.match_info["username"]
    log.debug("Stream for username='%s'", username)
    expressions = await expressions_for_user(
        request.app["db"], request.app["sparky"], username
    )
    context = {
        "settings": request.app["settings"],
        "username": username,
        "expressions": expressions,
        "current_user": request.user,
    }
    return request.app.render("stream/user.jinja2", request, context)


@found.transactional
async def stream(tr, sparky, user):
    """Fetch latest expressions of things that ``user`` follows"""
    log.debug("fetching stream")
    # TODO: Replace with an index directly in FDB
    patterns = (
        (sparky.var("follow"), "follower", user),
        (sparky.var("follow"), "followee", sparky.var("followee")),
        (sparky.var("expression"), "actor", sparky.var("followee")),
        (sparky.var("expression"), "html", sparky.var("html")),
        (sparky.var("expression"), "modified-at", sparky.var("modified-at")),
        (sparky.var("followee"), "name", sparky.var("name")),
    )
    out = await sparky.where(tr, *patterns)
    out.sort(key=lambda x: x["modified-at"], reverse=True)
    out = out[:100]
    return out


async def stream_get(request):
    expressions = await stream(
        request.app["db"], request.app["sparky"], request.user["uid"]
    )
    context = {"settings": request.app["settings"], "expressions": expressions}
    return request.app.render("stream/stream.jinja2", request, context)


@found.transactional
async def insert(tr, sparky, user, expression, html):
    now = int(time())
    uid = await sparky.uuid(tr)
    tuples = (
        (uid, "html", html),
        (uid, "expression", expression),
        (uid, "actor", user),
        (uid, "modified-at", now),
        (uid, "created-at", now),
    )
    await sparky.add(tr, *tuples)
    return uid


async def stream_post(request):
    data = await request.post()
    expression = data["expression"]
    log.debug("Post expression: %s", expression)
    cleaned = clean(expression.strip())
    if not cleaned:
        raise web.HTTPSeeOther(location="/stream/")
    html = markdown(cleaned)
    if html:
        await insert(
            request.app["db"],
            request.app["sparky"],
            request.user["uid"],
            expression,
            html,
        )
    raise web.HTTPSeeOther(location="/stream/")


@found.transactional
async def actor_by_name(tr, sparky, name):
    tuples = ((sparky.var("uid"), "name", name),)
    users = await sparky.where(tr, *tuples)
    assert len(users) == 1
    user = users[0]
    user = user.set("name", name)
    return user


async def follow_get(request):
    username = request.match_info["username"]
    log.debug("follow_get username=%r", username)
    user = await actor_by_name(request.app["db"], request.app["sparky"], username)
    context = {"settings": request.app["settings"], "user": user}
    return request.app.render("stream/follow.jinja2", request, context)


@found.transactional
async def follow(tr, sparky, user, other):
    other = await actor_by_name(tr, sparky, other)
    uid = await sparky.uuid(tr)
    tuples = ((uid, "follower", user["uid"]), (uid, "followee", other["uid"]))
    await sparky.add(tr, *tuples)


async def follow_post(request):
    username = request.match_info["username"]
    log.debug("follow_post username=%r", username)
    await follow(request.app["db"], request.app["sparky"], request.user, username)
    raise web.HTTPSeeOther(location="/stream/")
