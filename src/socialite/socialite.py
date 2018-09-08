#!/usr/bin/env python3
"""Usage:
  socialite run

Options:
  -h --help     Show this screen.
"""
import asyncio
import logging
import os
from uuid import UUID

import daiquiri
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

from socialite import settings
from socialite import fdb
from socialite import user
from socialite import stream
from socialite.filters import FILTERS
from socialite.helpers import no_auth


log = daiquiri.getLogger(__name__)


# middleware


async def middleware_check_auth(app, handler):
    """Check that the request has a valid token.

    Raise HTTPForbidden when the token is not valid.

    `handler` can be marked to ignore token. This is useful for pages like
    account login, account creation and password retrieval

    """
    async def middleware_handler(request):
        if getattr(handler, 'no_auth', False):
            response = await handler(request)
            return response
        else:
            try:
                token = request.cookies['token']
            except KeyError:
                log.debug('No auth token found')
                raise web.HTTPFound(location='/')
            else:
                max_age = app['settings'].TOKEN_MAX_AGE
                try:
                    uid = app['signer'].unsign(token, max_age=max_age)
                except SignatureExpired:
                    log.debug('Token expired')
                    raise web.HTTPFound(location='/')
                except BadSignature:
                    log.debug('Bad signature')
                    raise web.HTTPFound(location='/')
                else:
                    uid = uid.decode('utf-8')
                    uid = UUID(hex=uid)
                    document = await user.user_by_uid(request.app["db"], uid)
                    log.debug("User authenticated as '%s'", document["username"])
                    request.user = document
                    response = await handler(request)
                    return response

    return middleware_handler


# home

async def home(request):
    context = {'settings': request.app['settings']}
    return request.app.render('home.jinja2', request, context)


# status

@no_auth
async def status(request):
    """Check that the app is properly working"""
    return web.json_response('OK')


# boot the app

async def init_database(app):
    log.debug("init database")
    app['db'] = await fdb.open()
    return app


def create_app(loop):
    """Starts the aiohttp process to serve the REST API"""
    # setup logging
    level_name = os.environ.get('DEBUG', 'INFO')
    level = getattr(logging, level_name)
    daiquiri.setup(level=level, outputs=('stderr',))

    setproctitle('socialite')

    log.debug("boot")

    # init app
    app = web.Application()  # pylint: disable=invalid-name
    # jinja2
    templates = Path(__file__).parent / 'templates'
    setup_jinja2(
        app,
        loader=FileSystemLoader(str(templates)),
        filters=FILTERS,  # TODO: improve that stuff
    )
    # others
    app.render = render
    app.on_startup.append(init_database)
    app.middlewares.append(middleware_check_auth)
    app['settings'] = settings
    app['hasher'] = PasswordHasher()
    app['signer'] = TimestampSigner(settings.SECRET)
    app['session'] = ClientSession()

    # user routes
    app.router.add_route('GET', '/', user.login_get)
    app.router.add_route('POST', '/', user.login_post)
    # register
    app.router.add_route('GET', '/user/register', user.register_get)
    app.router.add_route('POST', '/user/register', user.register_post)
    # home route
    app.router.add_route('GET', '/home', home)
    # stream
    app.router.add_route('GET', '/stream/', stream.stream_get)
    app.router.add_route('POST', '/stream/', stream.stream_post)
    app.router.add_route('GET', '/stream/{username}', stream.items)
    app.router.add_route('GET', '/stream/{username}/follow', stream.follow_get)
    app.router.add_route('POST', '/stream/{username}/follow', stream.follow_post)
    # api route
    app.router.add_route('GET', '/api/status', status)

    return app


def main():
    """entry point of the whole application, equivalent to django's manage.py"""
    args = docopt(__doc__)
    setproctitle('socialite')

    if args.get('run'):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()
        app = create_app(loop)
        web.run_app(app, host='0.0.0.0', port=8000)
    else:
        print('Use --help to know more')


if __name__ == '__main__':
    main()
