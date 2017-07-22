all:
	@echo "Héllo, World!"

backend:
	python -m socialite.socialite web

lint:
	@pylint socialite
