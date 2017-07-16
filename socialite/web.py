"""Module defining the REST API"""
import asyncio

# import psycopg2
# import colander
import aiopg
from aiohttp import web

from setproctitle import setproctitle  # pylint: disable=no-name-in-module


@asyncio.coroutine
def status(request):
    """Check that the app is properly working"""
    return web.json_response('OK')


app = web.Application()  # pylint: disable=invalid-name
app.router.add_get('/api/status', status)


def main():
    """Starts the aiohttp process to serve the REST API"""
    setproctitle('socialite.py web')
    loop = asyncio.get_event_loop()
    # prepare app
    dsn = 'host=localhost port=5432 user=socialite password=socialite dbname=socialite'
    coroutine = aiopg.create_pool(dsn)
    app['aiopg'] = loop.run_until_complete(coroutine)
     # continue server bootstraping
    handler = app.make_handler()
    # FIXME: pass port as an argument
    coroutine = loop.create_server(handler, '0.0.0.0', 8080)
    server = loop.run_until_complete(coroutine)
    print('Serving on http://%s:%s' % server.sockets[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.run_until_complete(handler.finish_connections(1.0))
        loop.close()
