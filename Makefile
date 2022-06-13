DOCKER_IMAGE_NAME ?= django-docker-dev
PROJECT_PORT ?= 8500

lint:
	docker run -v ${CURDIR}:/apps alpine/flake8:latest .

deadcode:
	docker run -v ${CURDIR}:/apps registry.ubicast.net/docker/vulture:latest \
	--exclude *settings.py,*config.py,docker/,submodules/,logs/,data/ --min-confidence 90 --ignore-names user_modified,hints,fk_name,modeladmin .

test:
ifndef DOCKER
	docker run --rm -e "PYTEST_ARGS=${PYTEST_ARGS}" -v ${CURDIR}:/opt/src ${DOCKER_IMAGE_NAME} make test
else
	pytest --reuse-db --cov=homesite ${PYTEST_ARGS}
endif

run:
ifndef DOCKER
	docker run --rm -it -e DOCKER=1 -v ${CURDIR}:/opt/src -p ${PROJECT_PORT}:${PROJECT_PORT} ${DOCKER_IMAGE_NAME} make run
else
	bash docker/prepare.sh
	python3 homesite/manage.py runserver 0.0.0.0:${PROJECT_PORT}
endif

shell:
ifndef DOCKER
	docker run --rm -it -e DOCKER=1 -v ${CURDIR}:/opt/src ${DOCKER_IMAGE_NAME} make shell
else
	bash docker/prepare.sh
	bash
endif

django_shell:
ifndef DOCKER
	docker run --rm -it -e DOCKER=1 -v ${CURDIR}:/opt/src ${DOCKER_IMAGE_NAME} make django_shell
else
	bash docker/prepare.sh
	python3 homesite/manage.py shell
endif
