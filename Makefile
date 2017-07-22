all:
	@echo "Héllo, World!"

backend:
	adev runserver socialite/web.py --no-debug-toolbar

lint:
	@pylint socialite
