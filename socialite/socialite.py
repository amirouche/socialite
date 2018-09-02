#!/usr/bin/env python3
"""Usage:
  socialite run

Options:
  -h --help     Show this screen.
"""
import asyncio
import asyncpg
import daiquiri
import logging
import os

from aiohttp import web
from docopt import docopt
from pathlib import Path
from setproctitle import setproctitle  # pylint: disable=no-name-in-module

from . import settings


log = daiquiri.getLogger(__name__)


async def init(settings):
    log.info("init socilite, using %s", settings.DSN)


from string import punctuation

import asyncpg
import daiquiri
import trafaret as t
import async_timeout

from aiohttp import ClientSession
from aiohttp import web
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from feedparser import parse as feedparser
from itsdangerous import BadSignature
from itsdangerous import SignatureExpired
from itsdangerous import TimestampSigner
from setproctitle import setproctitle  # pylint: disable=no-name-in-module
from trafaret import DataError

from . import settings

# setup logging
log = daiquiri.getLogger(__name__)


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

# api


@no_auth
async def status(request):
    """Check that the app is properly working"""
    async with request.app['asyncpg'].acquire() as cnx:
        # introspect database
        query = """SELECT c.relname
        FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relkind = 'r'"""
        records = await cnx.fetch(query)
        for record in records:
            log.info(record)
    return web.json_response('OK!')


# account


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


@no_auth
async def account_new(request):
    """Create a new account raise bad request in case of error"""
    data = await request.json()
    try:
        data = account_new_validate(data)
    except t.DataError as exc:
        return web.json_response(exc.as_dict(), status=400)
    else:
        errors = dict()
        # check that the user is not already taken
        async with request.app['asyncpg'].acquire() as cnx:
            # TODO: try/except postgresql UniqueViolationError will be more
            # idiomatic
            # TODO: do that in transaction!
            query = 'SELECT COUNT(uid) FROM users WHERE username = $1;'
            count = await cnx.fetchval(query, data['username'])
            if count != 0:
                errors['username'] = 'There is already an user with that username'
            # check that the passwords are the same
            if data['password'] != data['validation']:
                errors['validation'] = 'Does not match password'
            # if there is an error return it otherwise, say it's ok
            if errors:
                return web.json_response(errors, status=400)

            password = request.app['hasher'].hash(data['password'])
            query = 'INSERT INTO users (username, password) VALUES ($1, $2)'
            await cnx.execute(query, data['username'], password)
            return web.json_response({})


@no_auth
async def account_login(request):
    """Try to login an user, return token if successful"""
    data = await request.json()
    # FIXME: validate and always report to the user that the login failed
    async with request.app['asyncpg'].acquire() as cnx:
        username = data['username']
        query = 'SELECT uid, password FROM users WHERE username = $1'
        row = await cnx.fetchrow(query, username)
        if row is None:
            return web.Response(status=401)
        else:
            try:
                request.app['hasher'].verify(row['password'], data['password'])
            except VerifyMismatchError:
                return web.Response(status=401)
            else:
                token = request.app['signer'].sign(str(row['uid']))
                token = token.decode('utf-8')
                out = dict(token=token)
            return web.json_response(out)


# others

async def check_auth(request):
    return web.json_response('OK')


# home

async def fetch(session, url):
    async with async_timeout.timeout(60):
        async with session.get(url) as response:
            return await response.text()


def get_entry_link(feed, link):
    try:
        t.URL(link)
    except DataError:
        return feed.feed.link + '/' + link
    else:
        return link


async def handle_show_feed(request, url):
    try:
        body = await fetch(request.app['session'], url)
    except Exception as exc:  # noqa
        return web.json_response({'kind': 'invalid url'})
    else:
        feed = feedparser(body)
        output = dict(title=feed.feed.title, entries=list())
        for entry in feed.entries:
            output['entries'].append(dict(
                title=entry.title,
                link=get_entry_link(feed, entry.link),
            ))
        return web.json_response(dict(kind='feed', output=output))


async def show_feed(request, input):
    try:
        t.URL(input)
    except DataError:
        return False, None
    else:
        return True, await handle_show_feed(request, input)


async def handle_add_feed(request, url, directory):
    try:
        body = await fetch(request.app['session'], url)
    except Exception as exc:  # noqa
        return web.json_response({'kind': 'invalid url'})
    else:
        with request.app['asyncpg'].cnx() as cnx:
            query = 'INSERT INTO subscriptions (username, password) VALUES ($1, $2)'
            await cnx.execute(query, data['username'], password)


async def add_feed(request, input):
    try:
        command, url, directory = input.split()
    except ValueError:
        return False, None
    else:
        if command != '/add':
            return False, None
        return True, handle_add_feed(request, url, directory)


HANDLERS = [
    show_feed,
    add_feed,
]


async def home(request):
    input = await request.json()
    if not input:  # retrieve summary
        return web.json_response({})
    else:  # otherwise, handle command
        for handler in HANDLERS:
            valid, output = await handler(request, input)
            if valid:
                return output
        return web.json_response({'kind': 'unknown'})


# boot the app

async def init_database(app):
    log.debug("init database")
    return app


def create_app(loop):
    """Starts the aiohttp process to serve the REST API"""
    setproctitle('socialite-api')

    log.debug("boot")

    # init app
    app = web.Application()  # pylint: disable=invalid-name
    app.on_startup.append(init_database)
    app.middlewares.append(middleware_check_auth)
    app['settings'] = settings
    app['hasher'] = PasswordHasher()
    app['signer'] = TimestampSigner(settings.SECRET)
    app['session'] = ClientSession()
    # routes
    app.router.add_route('GET', '/api/status', status)
    app.router.add_route('POST', '/api/check_auth', check_auth)
    # routes for account
    app.router.add_route('POST', '/api/account/new', account_new)
    app.router.add_route('POST', '/api/account/login', account_login)
    # route for home
    app.router.add_route('POST', '/api/home', home)

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
