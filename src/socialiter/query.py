import trafaret as t
from aiohttp import web

from socialiter import feed


async def query(request):
    try:
        query = request.query["query"]
    except KeyError:
        raise web.HTTPBadRequest()
    try:
        url = t.URL(query)
    except t.DataError:
        raise web.HTTPBadRequest(reason="Try an URL")
    try:
        out = await feed.parse(request.app["session"], url)
    except feed.UnknownFeedFormat:
        reason = "Feed format is not recognized"
        raise web.HTTPBadRequest(reason=reason)

    # nominal case
    context = {"settings": request.app["settings"], "feed": out, "url": url}
    return request.app.render("feed/home.jinja2", request, context)
