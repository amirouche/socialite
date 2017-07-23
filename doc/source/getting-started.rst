=================
 Getting started
=================

Install ``postgresql``, ``graphviz`` and ``rabbitmq-server`` using
your system package manager.

Create a ``socialite`` user with ``socialite`` password and
``socialite`` database. ``socialite`` must have all rights over
``socialite`` database::

  createdb socialite
  psql -c "CREATE USER socialite WITH PASSWORD 'socialite';"

Then install python dependencies::

  pip install requirements.txt

Before coding install ``pre-commit`` as git hook using the following
command::

  cp pre-commit .git/hooks/

If you want to force a commit (you need a good reason to do that>`_ use
commit with the ``-n`` option e.g. ``git commit -n``.

Also don't forget to install developement dependencies::

  pip install -r requirements.dev.txt

You prolly also want install `nvm <https://github.com/creationix/nvm>`_ to have
the correct nodejs version::

  wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.33.2/install.sh | bash

Currently the project is tested with nodejs v6.7.0.

Go inside the frontend directory and install frontend dependencies::

  npm install

Install ``jsdoc`` to be able to build the documentation::

  npm install -g jsdoc
