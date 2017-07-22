#!/usr/bin/env python3
"""Usage:
  socialite.py web

Options:
  -h --help     Show this screen.
"""
import asyncio

from aiohttp import web
from docopt import docopt
from setproctitle import setproctitle  # pylint: disable=no-name-in-module

from .web import create_app


def main():
    """entry point of the whole application, equivalent to django's manage.py"""
    args = docopt(__doc__)
    setproctitle('socialite')
    if args.get('web'):
        loop = asyncio.get_event_loop()
        app = create_app(loop)
        web.run_app(app, host='127.0.0.1', port=8000)
    else:
        print('Use --help to know more')


if __name__ == '__main__':
    main()
