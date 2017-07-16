#!/usr/bin/env python3
"""Usage:
  socialite.py web

Options:
  -h --help     Show this screen.
"""
from docopt import docopt
from setproctitle import setproctitle  # pylint: disable=no-name-in-module

from web import main as web


def main():
    """entry point of the whole application, equivalent to django's manage.pyx"""
    args = docopt(__doc__)
    setproctitle('socialite.py')
    if args.get('web'):
        web()
    else:
        print('Use --help to know more')


if __name__ == '__main__':
    main()
