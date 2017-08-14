"""Module defining the REST API"""
import logging
import os

from string import punctuation

import asyncpg
import daiquiri
import trafaret as t

from aiohttp import web
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from itsdangerous import BadSignature
from itsdangerous import SignatureExpired
from itsdangerous import TimestampSigner
from setproctitle import setproctitle  # pylint: disable=no-name-in-module

from . import settings

# setup logging
logger = daiquiri.getLogger(__name__)

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
                    username = app['signer'].unsign(token, max_age=max_age)
                except SignatureExpired:
                    raise web.HTTPForbidden(reason='auth token expired')
                except BadSignature:
                    raise web.HTTPForbidden(reason='bad signature')
                else:
                    request.username = username
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
            logger.info(record)
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
    username=t.String(min_length=1, max_length=255, regex=r'^[\w-]+$'),
    validation=t.String(),
    password=t.String(t.String(min_length=10, max_length=255) & strong_password),
    bio=t.String(allow_blank=True, max_length=1024),
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
            # FIXME: try/except UniqueViolationError will be more ideomatic
            query = 'SELECT COUNT(uid) FROM users WHERE username = $1;'
            count = await cnx.fetchval(query, data['username'])
            if count != 0:
                errors['username'] = 'There is already an user with that username'
            # check that the passwords are the same
            if data['password'] != data['validation']:
                errors['validation'] = 'Does not match password'
            # if there is an error return it otherwise, say it's ok
            # FIXME: use proper http status code
            if errors:
                return web.json_response(errors, status=400)

            password = request.app['hasher'].hash(data['password'])
            query = 'INSERT INTO users (username, password, bio) VALUES ($1, $2, $3)'
            await cnx.execute(query, data['username'], password, data['bio'])
            return web.json_response({})


@no_auth
async def account_login(request):
    """Try to login an user, return token if successful"""
    data = await request.json()
    # FIXME: validate and always report to the user that the login failed
    async with request.app['asyncpg'].acquire() as cnx:
        username = data['username']
        query = 'SELECT password FROM users WHERE username = $1'
        password = await cnx.fetchval(query, username)
        if password is None:
            return web.Response(status=401)
        else:
            try:
                request.app['hasher'].verify(password, data['password'])
            except VerifyMismatchError:
                return web.Response(status=401)
            else:
                token = request.app['signer'].sign(username)
                token = token.decode('utf-8')
                out = dict(token=token)
                return web.json_response(out)


async def check_auth(request):
    return web.json_response('OK')


# boot the app

async def init_pg(app):
    """Init asyncpg pool"""
    logger.debug("setup asyncpg, using %s", app['settings'].DSN)
    engine = await asyncpg.create_pool(app['settings'].DSN)
    app['asyncpg'] = engine
    return app


def create_app(loop):
    """Starts the aiohttp process to serve the REST API"""
    setproctitle('socialite-api')
    # setup logging
    level_name = os.environ.get('DEBUG', 'INFO')
    level = getattr(logging, level_name)
    daiquiri.setup(level=level, outputs=('stderr',))

    logger.debug("boot")

    # init app
    app = web.Application()  # pylint: disable=invalid-name
    app.on_startup.append(init_pg)
    app.middlewares.append(middleware_check_auth)
    app['settings'] = settings
    app['hasher'] = PasswordHasher()
    app['signer'] = TimestampSigner(settings.SECRET)

    #  routes
    app.router.add_route('GET', '/api/status', status)
    app.router.add_route('POST', '/api/account/new', account_new)
    app.router.add_route('POST', '/api/account/login', account_login)
    app.router.add_route('POST', '/api/check_auth', check_auth)

    return app
