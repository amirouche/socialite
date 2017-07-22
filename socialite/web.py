"""Module defining the REST API"""
import asyncio

import asyncpg
from aiohttp import web
from setproctitle import setproctitle  # pylint: disable=no-name-in-module


async def status(request):
    """Check that the app is properly working"""
    pg = request.app['postgresql']
    async with pg.acquire() as cnx:
        query = """SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE' AND table_schema = 'public'"""
        records = await cnx.fetch(query)
        for record in records:
            print(record)
    return web.json_response('OK!')


async def init_pg(app):
    """Init asyncpg pool"""
    dsn = 'postgres://socialite:socialite@localhost:5432/socialite'
    engine = await asyncpg.create_pool(dsn)
    app['postgresql'] = engine
    return app


def create_app(loop):
    """Starts the aiohttp process to serve the REST API"""
    setproctitle('socialite-web')
    app = web.Application()  # pylint: disable=invalid-name
    app.on_startup.append(init_pg)
    #  routes
    app.router.add_route('GET', '/api/status', status)
    return app
