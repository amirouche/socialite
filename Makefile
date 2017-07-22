all:
	@echo "Héllo, World!"

backend:
	adev runserver socialite/web.py --no-debug-toolbar

lint:
	@pylint socialite

database-repl:
	sudo -u postgres psql socialite

