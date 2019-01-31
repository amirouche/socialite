import logging
from urllib.parse import urlencode
from lxml.html import fromstring as string2html

from aiohttp import web


from socialiter.helpers import no_auth

log = logging.getLogger(__name__)


@no_auth
async def query(request):
    # validate
    try:
        user_query = request.query["query"]
    except KeyError:
        raise web.HTTPBadRequest()
    user_query = user_query.strip()
    if not user_query:
        raise web.HTTPBadRequest()

    #
    log.debug('user query is: %r', user_query)
    out = await bing(request.app, user_query)
    return web.json_response(out)

    # try:
    #     url = t.URL(query)
    # except t.DataError:
    #     raise web.HTTPBadRequest(reason="Try an URL")
    # try:
    #     out = await feed.parse(request.app["session"], url)
    # except feed.UnknownFeedFormat:
    #     reason = "Feed format is not recognized"
    #     raise web.HTTPBadRequest(reason=reason)

    # # nominal case
    # context = {"settings": request.app["settings"], "feed": out, "url": url}
    # return request.app.render("feed/home.jinja2", request, context)


async def bing(app, query):
    """Query bing.com for hits that match `query`"""
    base = "https://www.bing.com/search?"
    querystring = urlencode(dict(q=query))
    url = base + querystring
    response = await app["session"].get(url)
    if response.status == 200:
        string = await response.text()
        try:
            hits = _bing_parse(string)
        except Exception:
            log.exception("Failed to parse bing results: %r", response)
            return dict()
        else:
            out = dict(type="hits", hits=hits, query=query)
            return out
    else:
        log.error("Bing search failed: %r", response)
        return dict()


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
    description = result.xpath('.//*[@class="b_caption"]//p')[0]
    description = description.text_content()
    out = dict(title=title, url=url, description=description)
    log.debug("hit %r", out)
    return out
