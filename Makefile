all:
	@echo "Héllo, World!"

backend:
	./socialite/socialite.py web

lint:
	@pylint socialite
