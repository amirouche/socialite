#!/usr/bin/env python3
"""Usage:
  socialite run

Options:
  -h --help     Show this screen.
"""
import asyncio
import logging
import os

import daiquiri
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
from socialite.helpers import no_auth
from socialite import fdb


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
                token = request.headers['X-AUTH-TOKEN']
            except KeyError:
                raise web.HTTPForbidden(reason='auth token required')
            else:
                max_age = app['settings'].TOKEN_MAX_AGE
                try:
                    user_uid = app['signer'].unsign(token, max_age=max_age)
                except SignatureExpired:
                    log.debug('Token expired')
                    raise web.HTTPForbidden(reason='auth token expired')
                except BadSignature:
                    log.debug('Bad signature')
                    raise web.HTTPForbidden(reason='bad signature')
                else:
                    log.debug('User authenticated as {}'.format(user_uid))
                    request.user_uid = user_uid
                    response = await handler(request)
                    return response

    return middleware_handler


# index


@fdb.transactional
async def counter_get(tr):
    counter = await tr.get(b'counter')
    counter = fdb.unpack(counter)[0]
    return counter


@no_auth
async def index(request):
    app = request.app
    settings = request.app['settings']
    db = request.app['db']
    counter = await counter_get(db)
    context = dict(settings=settings, counter=counter)
    return app.render('index.jinja2', request, context)


@fdb.transactional
async def counter_increment(tr):
    counter = await counter_get(tr)
    counter += 1
    counter = fdb.pack((counter,))
    counter = tr.set(b'counter', counter)


@no_auth
async def increment(request):
    await counter_increment(request.app['db'])
    raise web.HTTPFound(location='/')


# api


@no_auth
async def status(request):
    """Check that the app is properly working"""
    return web.json_response('OK!')


# boot the app

@fdb.transactional
async def counter_init(tr):
    tr.set(b'counter', fdb.pack((0,)))


async def init_database(app):
    log.debug("init database")
    app['db'] = await fdb.open()
    await counter_init(app['db'])
    return app


def create_app(loop):
    """Starts the aiohttp process to serve the REST API"""
    setproctitle('socialite-api')

    log.debug("boot")

    # init app
    app = web.Application()  # pylint: disable=invalid-name
    # jinja2
    templates = Path(__file__).parent / 'templates'
    setup_jinja2(
        app,
        loader=FileSystemLoader(str(templates))
    )
    # others
    app.render = render
    app.on_startup.append(init_database)
    app.middlewares.append(middleware_check_auth)
    app['settings'] = settings
    app['hasher'] = PasswordHasher()
    app['signer'] = TimestampSigner(settings.SECRET)
    app['session'] = ClientSession()
    # frontend
    app.router.add_route('GET', '/', index)
    app.router.add_route('POST', '/', increment)
    # api
    app.router.add_route('GET', '/api/status', status)

    return app


def main():
    """entry point of the whole application, equivalent to django's manage.py"""
    args = docopt(__doc__)
    setproctitle('socialite')

    # setup logging
    level_name = os.environ.get('DEBUG', 'INFO')
    level = getattr(logging, level_name)
    daiquiri.setup(level=level, outputs=('stderr',))

    if args.get('run'):
        loop = asyncio.get_event_loop()
        app = create_app(loop)
        web.run_app(app, host='127.0.0.1', port=8000)
    else:
        print('Use --help to know more')


if __name__ == '__main__':
    main()
