#!/usr/bin/env python3
"""Usage:
  socialiter run

Options:
  -h --help     Show this screen.
"""
import asyncio
import logging
import os
from uuid import UUID

import daiquiri
import found
import found.sparky
import uvloop
from aiohttp import ClientSession
from aiohttp import web
from aiohttp_jinja2 import setup as setup_jinja2
from aiohttp_jinja2 import render_template as render
from argon2 import PasswordHasher

from docopt import docopt
from itsdangerous import BadSignature
from itsdangerous import SignatureExpired
from itsdangerous import TimestampSigner

from jinja2 import FileSystemLoader
from pathlib import Path
from setproctitle import setproctitle  # pylint: disable=no-name-in-module

from socialiter import beyond
from socialiter.beyond import h

from socialiter import settings
# from socialiter import feed
# from socialiter import query
# from socialiter import user
# from socialiter import stream
from socialiter.base import SpacePrefix


log = daiquiri.getLogger(__name__)


__version__ = (0, 0, 0)
VERSION = 'v' + '.'.join([str(x) for x in __version__])
HOMEPAGE = 'https://bit.ly/2D2fT5Q'


# status

async def status(request):
    """Check that the app is properly working"""
    return web.json_response('OK')


# boot the app

async def init_database(app):
    log.debug("init database")
    app['db'] = await found.open()
    app['sparky'] = found.sparky.Sparky(SpacePrefix.SPARKY.value)
    return app


def create_app(loop):
    """Starts the aiohttp process to serve the REST API"""
    # setup logging
    level_name = os.environ.get('DEBUG', 'INFO')
    level = getattr(logging, level_name)
    daiquiri.setup(level=level, outputs=('stderr',))

    setproctitle('socialiter')

    log.info("init socialiter %s", VERSION)

    # init app
    app = web.Application()  # pylint: disable=invalid-name
    # others
    app.on_startup.append(init_database)
    app['settings'] = settings
    app['hasher'] = PasswordHasher()
    app['signer'] = TimestampSigner(settings.SECRET)
    # setup HTTP session
    user_agent = 'socialiter {} ({})'.format(VERSION, HOMEPAGE)
    headers = {'User-Agent': user_agent}
    app['session'] = ClientSession(headers=headers)

    # api route
    app.router.add_route('GET', '/api/status', status)

    # beyond routes
    app.router.add_route('GET', '/websocket', beyond.websocket)
    app.router.add_route('GET', '/', beyond.index)
    app.router.add_route('GET', '/{path:.+}', beyond.index)

    # application routes
    app.handle = router = beyond.Router()

    async def index_init(event):
        model = {
            'conversation': [],
        }
        event.request.model = model
        for command in ['echo', 'alpha', 'bravo']:
            message = {'command': command, 'replies': {'echo': command}}
            event.request.model['conversation'].append(message)

    @beyond.beyond
    async def on_submit(event):
        message = {'command': 'form submit', 'replies': {'echo': 'y submit'}}
        event.request.model['conversation'].append(message)
        await event.token('fuuuuu')
        await event.redirect('/foobar')

    def index_render(model):
        log.debug('render chatbot: %r', model)
        shell = h.div(id="shell", Class="chatbot")

        shell.append(h.h1(style=beyond.Style(**{'background': 'red'}))["beyondjs"])

        for messages in model['conversation']:
            command = messages['command']
            replies = messages['replies']
            shell.append(h.p()[command])
            for chat, reply in replies.items():
                shell.append(h.p(Class='reply ' + chat)[chat + ': ' + reply])

        chatbox = h.div(id="chatbox")
        form = h.form(on_submit=on_submit)
        form.append(h.input(type="text"))
        form.append(h.input(type="submit"))
        chatbox.append(form)

        shell.append(chatbox)

        return shell

    router.add_route(r'^/$', index_init, index_render)

    return app


def main():
    args = docopt(__doc__)
    setproctitle('socialiter')

    if args.get('run'):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()
        app = create_app(loop)
        log.info('running webserver on http://0.0.0.0:8000')
        web.run_app(app, host='0.0.0.0', port=8000)  # nosec
    else:
        print('Use --help to know more')


if __name__ == '__main__':
    main()
