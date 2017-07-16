# Socialite

Socialite is:

- A social network kind of app that default to be private, that wants
  to have:

    - Bookmarks
    - Forum
    - Messaging
    - Search engine
    - Wiki
    
- A test bed for my experiments with aiohttp

- A test bed for my experiments with reactjs

- Yet another free software project


## Quick Links

- [socialite homepage](https://github.com/amirouche/socialite)
- [python 3.5](https://docs.python.org/3.5/)
- [aiohttp](http://aiohttp.readthedocs.io/en/stable/)
- [psycopg2](initd.org/psycopg/docs/)
- [yoyo migrations](https://pypi.org/project/yoyo-migrations/)


## Getting started

Install postgresql and rabbitmq using your system package
manager. Create a `socialite` user with `socialite` password and
`socialite` database. `socialite` must have all rights over
`socialite` database:

```sh
createdb socialite
psql -c "CREATE USER socialite WITH PASSWORD 'socialite';"
```

Then install python dependencies:

```sh
pip install requirements.txt
```

## Contributing

Before coding install `pre-commit` as git hook using the following
command:

```sh
cp pre-commit .git/hooks/
```

If you want to force a commit (you need a good reason to do that) use
commit with the `-n` option e.g. `git commit -n`.

Also don't forget to install developement dependencies:

```sh
pip install -r requirements.dev.txt
```

