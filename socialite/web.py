"""Module defining the REST API"""
import asyncio

from aiohttp import web
from setproctitle import setproctitle  # pylint: disable=no-name-in-module


@asyncio.coroutine
def status(request):
    """Check that the app is properly working"""
    return web.json_response('OK')


def create_app(loop):
    """Starts the aiohttp process to serve the REST API"""
    setproctitle('socialite-web')
    app = web.Application()  # pylint: disable=invalid-name
    #  routes
    app.router.add_route('GET', '/api/status', status)
    return app
