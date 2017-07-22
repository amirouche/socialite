all:
	@echo "Héllo, World!"

backend:
	adev runserver socialite/web.py --no-debug-toolbar > /dev/null

lint:
	@pylint socialite

database-repl:
	sudo -u postgres psql socialite

build-doc:
	cd doc && make html
	firefox doc/build/html/index.html
