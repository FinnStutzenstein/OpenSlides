# TESTS

run-system-tests:
	echo "TODO: write complete system tests"

run-service-tests:
	git submodule foreach 'make run-tests'

build-dev:
	git submodule foreach 'make build-dev'

run-dev: | build-dev
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
