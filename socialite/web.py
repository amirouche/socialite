"""Module defining the REST API"""
import os
import asyncio
import logging

import asyncpg
import daiquiri

from aiohttp import web
from setproctitle import setproctitle  # pylint: disable=no-name-in-module

from . import settings

# setup logging
logger = daiquiri.getLogger(__name__)


async def status(request):
    """Check that the app is properly working"""
    pg = request.app['postgresql']
    async with pg.acquire() as cnx:
        query = """SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE' AND table_schema = 'public'"""
        records = await cnx.fetch(query)
        for record in records:
            logger.info(record)
    return web.json_response('OK!')


async def init_pg(app):
    """Init asyncpg pool"""
    logger.debug("setup asyncpg, using %s", app['settings'].DSN)
    engine = await asyncpg.create_pool(app['settings'].DSN)
    app['postgresql'] = engine
    return app


def create_app(loop):
    """Starts the aiohttp process to serve the REST API"""
    setproctitle('socialite-web')
    # setup logging
    level_name = os.environ.get('DEBUG', 'INFO')
    level = getattr(logging, level_name)
    daiquiri.setup(level=level, outputs=('stderr',))

    logger.debug("boot")

    app = web.Application()  # pylint: disable=invalid-name
    app.on_startup.append(init_pg)
    app['settings'] = settings
    #  routes
    app.router.add_route('GET', '/api/status', status)
    return app
