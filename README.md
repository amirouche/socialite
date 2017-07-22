# Socialite

Socialite is:

- A social network kind of app that default to be private, that wants
  to have:

    - Blog
    - Bookmarks
    - Forum
    - Messaging
    - Search engine
    - Webmail
    - Wiki
    
- A test bed for my experiments with aiohttp

- A test bed for my experiments with reactjs

- Yet another free software project


## Quick Links

- [socialite homepage](https://github.com/amirouche/socialite)

Backend:

- [python 3.5](https://docs.python.org/3.5/)
- [aiohttp](http://aiohttp.readthedocs.io/en/stable/)
- [psycopg2](initd.org/psycopg/docs/)
- [yoyo migrations](https://pypi.org/project/yoyo-migrations/)

Frontend:

- [ReactJS](https://facebook.github.io/react/)
- [ImmutableJS](https://facebook.github.io/immutable-js/docs/)
- [flat ui colors](http://flatuicolors.com/)
- [flexbox guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)
- [css architecture](http://fixme)

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

You prolly also want install [nvm](https://github.com/creationix/nvm) to have
the correct nodejs version:

```sh
wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.33.2/install.sh | bash
```

Currently the project is tested with nodejs v6.7.0.
