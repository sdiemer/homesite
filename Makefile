DOCKER_IMAGE ?= homesite:latest
DOCKER_WORK_DIR ?= /opt/src
DOCKER_RUN ?= docker run --rm -it -v ${CURDIR}:${DOCKER_WORK_DIR} --name homesite
PROJECT_PORT ?= 8500


build:
	docker build -t ${DOCKER_IMAGE} ${BUILD_ARGS} \
		--build-arg USER_UID=$(shell id -u) \
		--build-arg USER_GID=$(shell id -g) \
		--build-arg DOCKER_WORK_DIR=${DOCKER_WORK_DIR} \
		.

rebuild:BUILD_ARGS = --no-cache
rebuild:build

push:
	docker push ${DOCKER_IMAGE}

pull:
	docker pull --quiet ${DOCKER_IMAGE}

lint:
	${DOCKER_RUN} ${DOCKER_IMAGE} lint_local

lint_local:
	flake8 homesite

typing:
	${DOCKER_RUN} ${DOCKER_IMAGE} typing_local

typing_local:
	mypy homesite

deadcode:
	${DOCKER_RUN} ${DOCKER_IMAGE} deadcode_local

deadcode_local:
	vulture --min-confidence 90 --ignore-names args,kwargs homesite

list_installed_files:
	${DOCKER_RUN} ${DOCKER_IMAGE} list_installed_files_local

list_installed_files_local:
	# List files installed by the Python package
	make clean
	python3 -m venv /tmp/venv
	cp -a ${DOCKER_WORK_DIR} /tmp/src
	cd /tmp/src && /tmp/venv/bin/pip install .
	cd /tmp/src && /tmp/venv/bin/pip show -f homesite

clean:
	rm -rf .coverage .pytest_cache .local .eggs build dist *.egg-info
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete

check_settings:
	test -f data/private/settings_override.py || echo ' \
		# Local settings \
		DEBUG = True \
		DEBUG_TOOLBAR = True \
		SESSION_COOKIE_SECURE = False \
		CSRF_COOKIE_SECURE = False \
		' > data/private/settings_override.py

run:check_settings
	echo 'Serving site on https://localhost:${PROJECT_PORT}'
	${DOCKER_RUN}-run -p ${PROJECT_PORT}:443 --user root ${DOCKER_IMAGE} run_local

run_local:
	rm -f /opt/homesite/data/tmp/*
	nginx -t
	# The systemctl command is not available here
	service nginx start
	/opt/homesite/venv/bin/homesite-control start --autoreload
	# Wait for log files to be ready
	sleep 1
	tail -f /opt/homesite/data/tmp/*.log

shell:
	${DOCKER_RUN} --entrypoint /bin/bash ${DOCKER_IMAGE}

django_shell:check_settings
	${DOCKER_RUN} ${DOCKER_IMAGE} django_shell_local

django_shell_local:
	python3 homesite/manage.py shell
