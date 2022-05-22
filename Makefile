setup: venv migrate user

venv: 
	python3 -m venv env
	./env/bin/pip install -r requirements.txt

run:
	./env/bin/python -m sprink.__init__

run-dev:
	./env/bin/adev runserver sprink/__init__.py

migrate:
	PYTHONPATH=./ ./env/bin/python scripts/migrate.py

user:
	PYTHONPATH=./ ./env/bin/python scripts/create_user.py