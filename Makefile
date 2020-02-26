# TESTS

run-system-tests:
	echo "TODO: write complete system tests"

run-service-tests:
	git submodule foreach 'make run-tests'

build-dev:
	git submodule foreach 'make build-dev'
	make -C haproxy build-dev

run-dev: | build-dev
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml -p 127.0.0.1:8000:8000/tcp up

build-prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

run-prod: | build-prod
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml -p 127.0.0.1:8000:8000/tcp up
