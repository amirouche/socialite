#!/usr/bin/env python3
"""Usage:
  socialiter run

Options:
  -h --help     Show this screen.
"""
import asyncio
import logging
import os
import trafaref as t
from string import punctuation

import daiquiri
import found
import found.sparky
import uvloop
from aiohttp import ClientSession
from aiohttp import web
from argon2 import PasswordHasher

from docopt import docopt
from itsdangerous import TimestampSigner
from itsdangerous import BadSignature
from itsdangerous import SignatureExpired

from setproctitle import setproctitle  # pylint: disable=no-name-in-module

from socialiter import settings
from socialiter.base import SpacePrefix


log = daiquiri.getLogger(__name__)


__version__ = (0, 0, 0)
VERSION = "v" + ".".join([str(x) for x in __version__])
HOMEPAGE = "https://bit.ly/2D2fT5Q"


# middleware

def no_auth(handler):
    """Decorator to tell the ``middleware_check_auth`` to not check for the token

    """
    handler.no_auth = True
    return handler


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


# status

@no_auth
async def status(request):
    """Check that the app is properly working"""
    return web.json_response("OK")


# api/v0

async def check_auth(request):
    return web.json_response('OK')


def strong_password(string):
    """Check that ``string`` is strong enough password"""
    if (any(char.isdigit() for char in string)
            and any(char.islower() for char in string)
            and any(char.isupper() for char in string)
            and any(char in punctuation for char in string)):
        return string
    else:
        raise t.DataError('Password is not strong enough')


account_new_validate = t.Dict(
    username=t.String(min_length=1, max_length=255) & t.Regexp(r'^[\w-]+$'),
    password=t.String(min_length=10, max_length=255) & strong_password,
    validation=t.String(),
)


# boot the app

async def init_database(app):
    log.debug("init database")
    app["db"] = await found.open()
    app["main"] = found.sparky.Sparky(SpacePrefix.MAIN.value)
    return app


def create_app(loop):
    """Starts the aiohttp process to serve the REST API"""
    # setup logging
    level_name = os.environ.get("DEBUG", "INFO")
    level = getattr(logging, level_name)
    daiquiri.setup(level=level, outputs=("stderr",))

    setproctitle("socialiter")

    log.info("init socialiter %s", VERSION)

    # init app
    app = web.Application()
    app.on_startup.append(init_database)
    app.middlewares.append(middleware_check_auth)
    app["settings"] = settings
    app["hasher"] = PasswordHasher()
    app["signer"] = TimestampSigner(settings.SECRET)
    user_agent = "socialiter {} ({})".format(VERSION, HOMEPAGE)
    headers = {"User-Agent": user_agent}
    app["session"] = ClientSession(headers=headers)

    # routes
    app.router.add_route("GET", "/api/status", status)
    app.router.add_route("GET", "/api/v0/user/authenticate", user_authenticate)
    app.router.add_route('GET', '/api/v0/user/check', user_check)
    app.router.add_route('POST', '/api/v0/user/create', user_create)

    # that's all folks
    return app


def main():
    """entry point of the whole application, equivalent to django's manage.py"""
    args = docopt(__doc__)
    setproctitle("socialiter")

    if args.get("run"):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()
        app = create_app(loop)
        log.info("running webserver on http://0.0.0.0:8000")
        web.run_app(app, host="0.0.0.0", port=8000)  # nosec
    else:
        print("Use --help to know more")


if __name__ == "__main__":
    main()
