.PHONY: help

.DEFAULT_GOAL := help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

run-front: ## Run the frontend server
	cd frontend && npm start

run-api: ## Run the backend api server
	DEBUG=DEBUG adev runserver socialite/api.py --no-debug-toolbar

run-init: ## Run initialisation
	DEBUG=DEBUG python -m socialite.socialite init


lint: ## lint the code
	@pylint socialite

database-repl: ## start a repl for the database
	pgcli socialite socialite -h localhost --less-chatty

database-reset: ## Kill any (known) processus using the database, drop and recreate the database and run migrations
	killall socialite-api || true
	sudo -u postgres dropdb socialite
	sudo -u postgres createdb socialite
	python -m socialite.socialite database migrate

database-diagram: ## Generate database Entity-Relationship diagram and run 'eog'
	python -m socialite.socialite database diagram
	eog socialite-diagram.png

database-schema: ## Output the current schema
	sudo -u postgres pg_dump -s socialite

build-doc:  ## Build the documentation and run 'firefox'
	cd doc && make html
	firefox doc/build/html/index.html

upstream:  ## Clone the most important third-party libraries
	mkdir upstream
	git clone https://github.com/MagicStack/asyncpg upstream/asyncpg
	git clone https://github.com/aio-libs/aiohttp upstream/aiohttp
	hg clone https://bitbucket.org/ollyc/yoyo upstream/yoyo
	git clone https://github.com/Deepwalker/trafaret upstream/trafaret
