#!/usr/bin/env python3
"""Usage:
  socialite database diagram
  socialite database migrate
  socialite init
  socialite web

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
from eralchemy import render_er
from pathlib import Path
from setproctitle import setproctitle  # pylint: disable=no-name-in-module
from yoyo.scripts.main import main as yoyo

from . import settings
from .api import create_app


log = daiquiri.getLogger(__name__)


async def init(settings):
    log.info("setup asyncpg, using %s", settings.DSN)
    engine = await asyncpg.create_pool(settings.DSN)
    async with engine.acquire() as cnx:
        pass


def main():
    """entry point of the whole application, equivalent to django's manage.py"""
    args = docopt(__doc__)
    setproctitle('socialite')

    # setup logging
    level_name = os.environ.get('DEBUG', 'INFO')
    level = getattr(logging, level_name)
    daiquiri.setup(level=level, outputs=('stderr',))

    if args.get('web'):
        loop = asyncio.get_event_loop()
        app = create_app(loop)
        web.run_app(app, host='127.0.0.1', port=8000)
    elif args.get('init'):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(init(settings))
    elif args.get('database') and args.get('migrate'):
        directory = Path(__file__) / '..' / 'migrations'
        directory = directory.resolve()
        directory = str(directory)
        yoyo([
            '--no-config-file',
            '-b',
            'apply',
            '--database',
            settings.DSN,
            directory,
        ])
    elif args.get('database') and args.get('diagram'):
        render_er(settings.DSN, 'socialite-diagram.png')
    else:
        print('Use --help to know more')


if __name__ == '__main__':
    main()
