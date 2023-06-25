.PHONY: init-pipenv
	echo "Python virtual environemnt initialization step started"
	pip install pipenv
	pipenv install || pipenv sync

.PHONY: init-db
	echo "Database initialization step started"
	flask db init
	flask db upgrade

init : init-pipenv init-db


run :
	flask run --host=127.0.0.1 --port=8000
