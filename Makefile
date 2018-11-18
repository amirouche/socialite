help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

dev: ## Prepare the host sytem for development
	wget https://www.foundationdb.org/downloads/6.0.15/ubuntu/installers/foundationdb-clients_6.0.15-1_amd64.deb
	sudo dpkg -i foundationdb-clients_6.0.15-1_amd64.deb
	wget https://www.foundationdb.org/downloads/6.0.15/ubuntu/installers/foundationdb-server_6.0.15-1_amd64.deb
	sudo dpkg -i foundationdb-server_6.0.15-1_amd64.deb
	pip3 install pipenv==2018.10.13
	pipenv install --dev --skip-lock
	pipenv run pre-commit install

check: ## Run tests
	make database-clean
	pipenv run py.test -vv --capture=no src/tests/
	pipenv check
	bandit --skip=B101 -r src/
	@echo "\033[95m\n\nYou may now run 'make lint' or 'make coverage'.\n\033[0m"

check-coverage: ## Code coverage
	make database-clean
	pipenv run py.test -vv --cov-config .coveragerc --cov-report term --cov-report html --cov-report xml --cov=src src/tests/

devrun: ## Run application in development mode
	cd src && DEBUG=DEBUG adev runserver --livereload --static socialiter/static/ socialiter/main.py

lint: ## Lint the code
	pipenv run pylint src/  # TODO: replace with lama

doc: ## Build the documentation
	cd src/doc && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at src/doc/_build/html/index.html.\n\033[0m"

upstream: ## Clone the most important third-party libraries
	mkdir upstream
	git clone https://github.com/aio-libs/aiohttp upstream/aiohttp
	git clone https://github.com/Deepwalker/trafaret upstream/trafaret

clean: ## Clean up
	git clean -fX

database-clean:  ## Remove all data from the database
	fdbcli --exec "writemode on; clearrange \x00 \xFF;"

todo: ## Things that should be done
	@grep -nR --color=always TODO src/

xxx: ## Things that require attention
	@grep -nR --color=always --before-context=2  --after-context=2 XXX src/
