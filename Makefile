DOCKER_IMAGE_NAME ?= django-docker-dev
PROJECT_PORT ?= 8500

lint:
	docker run -v ${CURDIR}:/apps registry.ubicast.net/docker/flake8:latest flake8 .

deadcode:
	docker run -v ${CURDIR}:/apps registry.ubicast.net/docker/vulture:latest \
		vulture --exclude *settings.py,*config.py,docker/,submodules/,logs/,data/ --min-confidence 90 --ignore-names user_modified,hints,fk_name,modeladmin .

test:
	docker run --rm -e "PYTEST_ARGS=${PYTEST_ARGS}" -v ${CURDIR}:/opt/src ${DOCKER_IMAGE_NAME} make test_local

test_local:
	pytest --reuse-db --cov=homesite ${PYTEST_ARGS}

run:
	docker run --rm -it -v ${CURDIR}:/opt/src -p ${PROJECT_PORT}:${PROJECT_PORT} ${DOCKER_IMAGE_NAME} make run_local

run_local:
	bash docker/prepare.sh
	python3 homesite/manage.py runserver 0.0.0.0:${PROJECT_PORT}

shell:
	docker run --rm -it -v ${CURDIR}:/opt/src ${DOCKER_IMAGE_NAME} make shell_local

shell_local:
	bash docker/prepare.sh
	bash

django_shell:
	docker run --rm -it -v ${CURDIR}:/opt/src ${DOCKER_IMAGE_NAME} make shell_local_local

shell_local_local:
	bash docker/prepare.sh
	python3 homesite/manage.py shell
