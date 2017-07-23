#!/usr/bin/env python3
"""Usage:
  socialite web
  socialite database migrate

Options:
  -h --help     Show this screen.
"""
import asyncio
from pathlib import Path

from aiohttp import web
from docopt import docopt
from setproctitle import setproctitle  # pylint: disable=no-name-in-module
from yoyo.scripts.main import main as yoyo

from . import settings
from .api import create_app


def main():
    """entry point of the whole application, equivalent to django's manage.py"""
    args = docopt(__doc__)
    setproctitle('socialite')
    if args.get('web'):
        loop = asyncio.get_event_loop()
        app = create_app(loop)
        web.run_app(app, host='127.0.0.1', port=8000)
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
    else:
        print('Use --help to know more')


if __name__ == '__main__':
    main()
