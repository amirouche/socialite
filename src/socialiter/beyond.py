"""BeyondJS is backend framework for building rich internet
application without writing javascript

"""
import os
import logging
import re
from collections import namedtuple
from functools import wraps
from json import dumps
from json import loads
from uuid import uuid4

import aiohttp
from aiohttp import web
from markupsafe import escape

log = logging.getLogger(__name__)


class BeyondException(Exception):
    pass


def generate_unique_key(dictionary):
    key = uuid4().hex
    if key not in dictionary:
        return key
    raise BeyondException('Seems like the dictionary is full')


class Node(object):  # inspired from nevow
    """Python representaiton of html nodes.

    Text nodes are python strings.

    You must not instantiate this class directly. Instead use the
    global instance `h` of the `PythonHTML` class.

    """

    __slots__ = ('_tag', '_children', '_attributes')

    def __init__(self, tag):
        self._tag = tag
        self._children = list()
        self._attributes = dict()

    def __call__(self, **kwargs):
        """Update node's attributes"""
        self._attributes.update(kwargs)
        return self

    def __repr__(self):
        return '<Node: %s %s>' % (self._tag, self._attributes)

    def append(self, node):
        """Append a single node or string as a child"""
        if not isinstance(node, Node):
            node = escape(node)
        self._children.append(node)

    def extend(self, nodes):
        [self.append(node) for node in nodes]

    def __getitem__(self, node):
        """Add nodes as children"""
        # XXX: __getitem__ is implemented in terms of `Node.append`
        # so that widgets can simply inherit from node and override
        # self.append with the bound `Node.append`.
        self.append(node)
        return self


def serialize(node):
    """Convert a `Node` hierarchy to a json string.

    Returns two values:

    - the dict representation
    - an event dictionary mapping event keys to callbacks

    """

    events = dict()

    def to_html_attributes(attributes):
        """Filter and convert attributes to html attributes"""
        for key, value in attributes.items():
            if key.startswith('on_'):
                pass
            elif key == 'Class':
                yield 'class', value
            elif key == 'For':
                yield 'for', value
            else:
                yield key, value

    def to_html_events(attributes):
        """Filter and rename attributes referencing callbacks"""
        for key, value in attributes.items():
            if key.startswith('on_'):
                yield key[3:], value

    def to_dict(node):
        """Recursively convert `node` into a dictionary"""
        if isinstance(node, (str, float, int)):
            return node
        else:
            out = dict(tag=node._tag)
            out['attributes'] = dict(to_html_attributes(node._attributes))
            on = dict()
            for event, callback in to_html_events(node._attributes):
                key = generate_unique_key(events)
                events[key] = callback  # XXX: side effect!
                on[event] = key
            if on:
                out['on'] = on
            out['children'] = [to_dict(child) for child in node._children]
            return out

    return to_dict(node), events


class PythonHTML(object):
    """Sugar syntax for creating `Node` instance.

    E.g.

    h.div(id="container", Class="minimal thing", For="something")["Héllo World!"]

    container = h.div(id="container", Class="minimal thing")
    container.append("Héllo World!")

    """

    def form(self, **kwargs):
        """form element that prevents default 'submit' behavior"""
        node = Node('form')
        node._attributes['onsubmit'] = 'return false;'
        node._attributes.update(**kwargs)
        return node

    def input(self, **kwargs):
        type = kwargs.get('type')
        if type == 'text':
            # XXX: hack to workaround snabbdom issue 401
            try:
                kwargs['id']
            except KeyError:
                pass
            else:
                log.warning("id attribute on text input node ignored")
            node = Node('input#' + uuid4().hex)
        else:
            node = Node('input')
        node._attributes.update(**kwargs)
        return node

    def __getattr__(self, attribute_name):
        return Node(attribute_name)


h = PythonHTML()


def beyond(callable):
    """There is something beyond javascript ;)"""

    @wraps(callable)
    async def wrapper(*args):
        # execute event handler
        await callable(*args)
        # re-render the page
        event = args[-1]
        html = await event.request.app.handle(event)
        # serialize the html and extract event handlers
        html, events = serialize(html)
        # update events handlers
        event.websocket.events = events
        # send html update
        msg = dict(
            html=html,
        )
        await event.websocket.send_str(dumps(msg))

    return wrapper


class Event:

    __slot__ = ('type', 'request', 'websocket', 'payload')

    def __init__(self, type, request, websocket, payload):
        self.type = type
        self.request = request
        self.websocket = websocket
        self.payload = payload

    def __repr__(self):
        return '<Event {} {}>'.format(self.type, self.payload)

    async def redirect(self, path):
        await self.websocket.send_json(dict(type='location-update', pathname=path))

    async def token(self, value=None):
        await self.websocket.send_json(dict(type='token-update', token=value))


async def websocket(request):
    """websocket handler"""
    websocket = web.WebSocketResponse()
    await websocket.prepare(request)

    async for msg in websocket:
        if msg.type == aiohttp.WSMsgType.ERROR:
            msg = 'websocket connection closed with exception %s'
            msg = msg % websocket.exception()
            log.warning(msg)
        elif msg.type == aiohttp.WSMsgType.CLOSE:
            break
        elif msg.type == aiohttp.WSMsgType.TEXT:
            event = loads(msg.data)
            log.debug('websocket got message type: %s', event["type"])
            if event['type'] == 'init':
                # Render the page
                event = Event('init', request, websocket, event)
                html = await request.app.handle(event)
                # serialize html and extract event handlers
                html, events = serialize(html)
                # update event handlers
                websocket.events = events
                # send html update
                msg = dict(type='dom-update', html=html)
                await websocket.send_str(dumps(msg))
            elif event['type'] == 'dom-event':
                # Build backend event
                key = event['key']
                event = Event('dom-event', request, websocket, event)
                # retrieve callback for event
                callback = websocket.events[key]
                # exec, prolly sending back a response via event.websocket
                await callback(event)
                # render page
                html = await request.app.handle(event)
                # serialize html and extract event handlers
                html, events = serialize(html)
                # update event handlers
                websocket.events = events
                # send html update
                msg = dict(type='dom-update', html=html)
                await websocket.send_str(dumps(msg))
            else:
                msg = "msg type '%s' is not supported yet" % msg['type']
                raise NotImplementedError(msg)
        else:
            raise NotImplementedError(msg)

    log.debug('websocket connection closed')

    return websocket


async def index(request):
    """Return the index page"""
    filepath = os.path.join(os.path.dirname(__file__), 'index.html')
    with open(filepath, 'rb') as f:
        return web.Response(body=f.read(), content_type='text/html')


Route = namedtuple('Route', ('regex', 'init', 'handler'))


class Router:
    """Why yet another router..."""

    def __init__(self):
        self._routes = list()

    def add_route(self, pattern, init, handler):
        regex = re.compile(pattern)
        route = Route(regex, init, handler)
        self._routes.append(route)

    async def __call__(self, event):
        log.debug("new event %r", event)
        path = event.payload['path']
        log.debug('routing path: %s' % path)
        for route in self._routes:
            match = route.regex.match(path)
            if match is not None:
                # This is a match
                args = match.groups()
                log.debug('Match found %r with args=%r', route, args)
                if event.type == 'init':
                    await route.init(event, *args)
                assert getattr(event.request, 'model'), "model must be set in route init function"
                html = route.handler(event.request.model)
                return html
        else:
            # Ark! The route is not defined! Error 404 wanna be.
            return h.h1()['beyondjs: no route found']

# <3
