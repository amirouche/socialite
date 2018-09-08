# socialite - wanna be private-first social network

[![travis](https://api.travis-ci.com/amirouche/socialite.svg?branch=master)](https://travis-ci.com/amirouche/socialite) [![codecov](https://codecov.io/gh/amirouche/socialite/branch/master/graph/badge.svg)](https://codecov.io/gh/amirouche/socialite)

socialite is proof-of-concept social network that experiments various
backend architectural choices.

<!-- It takes inspiration from peer-to-peer systems ideas and apply them in the context of controlled environments. -->

socialite is built using the Model-View-Controller pattern on top of
[aiohttp](https://aiohttp.readthedocs.io/en/stable/). The
[jinja2](http://jinja.pocoo.org/) library is used for rendering the
view.

socialite wants to proove that a complex application can be developed
and operated more easily as a monolithic service using the right
abstractions and expert systems. That's why socialite use
[FoundationDB](https://apple.github.io/foundationdb/) and does not use
REDIS.

<!-- socialite experiment with an innovative [distributed **priority** task -->
<!-- queue](https://github.com/amirouche/socialite/issues/14). The goal of -->
<!-- that particular component is to ease operation of the application. -->

## Styles Style Guide

- Do no rely on LESS or SASS
- Only rely on classes and tags
- Avoid class when tag is sufficent to disambiguate
- Prefix class names with component name to avoid any leak
- Avoid cascade ie. all styles must appear in the class declaration
- When it makes sens, be precise in the selector (most of the time it must start with `#root.root-class`)
