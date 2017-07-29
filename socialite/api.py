"""Module defining the REST API"""
import asyncio
import logging
import os

from string import punctuation

import asyncpg
import daiquiri

from aiohttp import web
from argon2 import PasswordHasher
from setproctitle import setproctitle  # pylint: disable=no-name-in-module
import trafaret as t

from . import settings

# setup logging
logger = daiquiri.getLogger(__name__)


# api

async def status(request):
    """Check that the app is properly working"""
    async with request.app['asyncpg'].acquire() as cnx:
        query = """SELECT c.relname
        FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relkind = 'r'"""
        records = await cnx.fetch(query)
        for record in records:
            logger.info(record)
    return web.json_response('OK!')


def strong_password(string):
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
            if errors:
                return web.json_response(errors, status=400)
            else:
                password = request.app['hasher'].hash(data['password'])
                query = 'INSERT INTO users (username, password, bio) VALUES ($1, $2, $3)'
                await cnx.execute(query, data['username'], password, data['bio'])
        return web.json_response({})


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

    app = web.Application()  # pylint: disable=invalid-name
    app.on_startup.append(init_pg)
    app['settings'] = settings
    app['hasher'] = PasswordHasher()
    #  routes
    app.router.add_route('GET', '/api/status', status)
    app.router.add_route('POST', '/api/account/new', account_new)
    return app
