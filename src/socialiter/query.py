import logging
from urllib.parse import urlencode
from lxml.html import fromstring as string2html

import trafaret as t
from aiohttp import web

from socialiter import feed


log = logging.getLogger(__name__)


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


async def bing(app, query):
    """Query bing.com for hits that match `query`"""
    base = "https://www.bing.com/search?q="
    url = base + urlencode(query)
    response = await app["session"].get(url)
    if response.status == 200:
        string = await response.text()
        try:
            hits = _bing_parse(string)
        except Exception:
            log.exception("Failed to parse bing results: %r", response)
            return list()
        else:
            return hits
    else:
        log.error("Bing search failed: %r", response)
        return list()


def _bing_parse(string):
    out = []
    html = string2html(string)
    results = html.xpath('//ol[@id="b_results"]/li[@class="b_algo"]')
    for result in results:
        hit = _bing_parse_one(result)
        out.append(hit)
    return out


def _bing_parse_one(result):
    title = result.xpath(".//h2/a/text()")[0]
    url = result.xpath(".//h2/a/@href")[0]
    description = result.xpath('.//*[@class="b_caption"]//p/text()')[0]
    return dict(title=title, url=url, description=description)
