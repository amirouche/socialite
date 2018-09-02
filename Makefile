.PHONY: help doc

install:
	# install FoundationDB
	wget https://www.foundationdb.org/downloads/5.2.5/ubuntu/installers/foundationdb-clients_5.2.5-1_amd64.deb
	sudo dpkg -i foundationdb-clients_5.2.5-1_amd64.deb
	wget https://www.foundationdb.org/downloads/5.2.5/ubuntu/installers/foundationdb-server_5.2.5-1_amd64.deb
	sudo dpkg -i foundationdb-server_5.2.5-1_amd64.deb
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock

check:
	pipenv run py.test --capture=no tests.py

coverage:
	pipenv run py.test --cov-config .coveragerc --verbose --cov-report term --cov-report html --cov-report xml --cov=socialite tests.py

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

	devrun: ## Run application in development mode
	DEBUG=DEBUG adev runserver socialite/socialite.py --no-debug-toolbar

lint: ## lint the code
	pipenv run pylint socialite

doc:  ## Build the documentation
	cd doc && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at doc/_build/html/index.html.\n\033[0m"

upstream:  ## Clone the most important third-party libraries
	mkdir upstream
	git clone https://github.com/aio-libs/aiohttp upstream/aiohttp
	git clone https://github.com/Deepwalker/trafaret upstream/trafaret

clean:  ## Clean things up
	find . -name '*.~' -exec rm --force {} +
