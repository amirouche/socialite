help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

init: ## Prepare the host sytem for development
	wget https://www.foundationdb.org/downloads/6.0.15/ubuntu/installers/foundationdb-clients_6.0.15-1_amd64.deb
	sudo dpkg -i foundationdb-clients_6.0.15-1_amd64.deb
	wget https://www.foundationdb.org/downloads/6.0.15/ubuntu/installers/foundationdb-server_6.0.15-1_amd64.deb
	sudo dpkg -i foundationdb-server_6.0.15-1_amd64.deb
	pip3 install --upgrade pipenv==2018.10.13
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev --skip-lock
	pipenv run pre-commit install --hook-type pre-push
	@echo "\033[95m\n\nYou may now run 'pipenv shell'.\n\033[0m"

check: ## Run tests
	make database-clear
	PYTHONHASHSEED=0 PYTHONPATH=$(PWD)/src/ pipenv run py.test -vvv --cov-config .coveragerc --cov-report html --cov-report xml --cov=socialiter src/tests/
	pipenv check
	pipenv run bandit --skip=B101 src/
	@echo "\033[95m\n\nYou may now run 'make lint'.\n\033[0m"

devrun: ## Run application in development mode
	cd src && DEBUG=DEBUG adev runserver --livereload --static socialiter/static/ socialiter/main.py

lint: ## Lint the code
	pipenv run pylama src/

doc: ## Build the documentation
	cd src/doc && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at src/doc/_build/html/index.html.\n\033[0m"

database-clear:  ## Remove all data from the database
	fdbcli --exec "writemode on; clearrange \x00 \xFF;"

todo: ## Things that should be done
	@grep -nR --color=always TODO src/

xxx: ## Things that require attention
	@grep -nR --color=always --before-context=2  --after-context=2 XXX src/

repl: ## ipython REPL inside source directory
	cd src && ipython
