all:
	@echo "Héllo, World!"

backend:
	adev runserver socialite/api.py --no-debug-toolbar > /dev/null

lint:
	@pylint socialite

database-repl:
	pgcli socialite socialite -h localhost --less-chatty

database-reset:
	sudo -u postgres dropdb socialite
	sudo -u postgres createdb socialite

database-diagram:
	python -m socialite.socialite database diagram
	eog socialite-diagram.png

database-schema:
	sudo -u postgres pg_dump -s socialite

build-doc:
	cd doc && make html
	firefox doc/build/html/index.html

upstream:
	mkdir upstream
	git clone https://github.com/MagicStack/asyncpg upstream/asyncpg
	git clone https://github.com/aio-libs/aiohttp upstream/aiohttp
	hg clone https://bitbucket.org/ollyc/yoyo upstream/yoyo
