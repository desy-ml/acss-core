UNAME=$(shell uname -m)
ENV_FILE=.env
SERVICE = ""

build:
	docker-compose --env-file $(ENV_FILE) -p pipeline build


build-kafka-images:
ifeq ($(UNAME),x86_64)
	docker build --no-cache -t acss/kafka-broker:1.0.0 -f external/kafka-docker/Dockerfile external/kafka-docker/ 
	docker build --no-cache -t acss/zookeeper:3.7.0 -f docker/zookeeper.x86_64.Dockerfile .
else
	docker build --no-cache -t acss/kafka-broker:1.0.0 -f external/kafka-docker/arm64.Dockerfile external/kafka-docker/ 
	docker build --no-cache -t acss/zookeeper:3.7.0 -f docker/zookeeper.arm64.Dockerfile .
endif

build-service-images:
	docker build -t acss/acss_core:latest -f docker/acss_core.Dockerfile .
	docker build -t acss/core_service:latest -f docker/core_service.Dockerfile .
	docker build -t acss/http_iface:latest -f docker/http_iface.Dockerfile .
	docker build -t acss/service:latest -f docker/service.Dockerfile .
	docker build -t acss/test:latest -f docker/test.Dockerfile .

build-base-images:
	docker build -t acss/acss-base -f docker/base.Dockerfile .
	docker build -t acss/acss-base-server -f docker/base.server.Dockerfile .

build-all: build-kafka-images build-base-images build-service-images build

unit-tests: test-up
	docker-compose -p pipeline run --rm --no-deps --entrypoint="/pipe/.venv/bin/python -m pytest tests/unit" test_api

integration-tests: test-up
	docker-compose -p pipeline ps 
	docker-compose -p pipeline run --rm --no-deps --entrypoint="/pipe/.venv/bin/python -m pytest tests/integration" test_api 

e2e-tests: test-up
	docker-compose -p pipeline run --rm --no-deps --entrypoint="/pipe/.venv/bin/python -m pytest tests/e2e" test_api

e2e-tests-external:
	docker-compose --env-file $(ENV_FILE) -p pipeline --profile testing up -d --no-deps
	docker-compose --env-file $(ENV_FILE) -p pipeline run --rm --no-deps --entrypoint="/pipe/.venv/bin/python -m pytest tests/e2e/start_up_test.py" test_api
	docker-compose --env-file $(ENV_FILE) -p pipeline run --rm --no-deps --entrypoint="/pipe/.venv/bin/python -m pytest tests/integration" test_api 	

test: test-up
	docker-compose --env-file $(ENV_FILE) -p pipeline run --rm --no-deps --entrypoint="/pipe/.venv/bin/python -m pytest tests" test_api

test-up:
	docker-compose --env-file $(ENV_FILE) -p pipeline --profile core --profile testing --profile at --profile simulation up -d
	docker-compose -p pipeline ps

prod-sim:
	docker-compose --env-file $(ENV_FILE) -p pipeline --profile core --profile prod --profile at --profile simulation up -d
	docker-compose -p pipeline ps


up:
	docker-compose --env-file $(ENV_FILE) --profile core --profile at --profile simulation -p pipeline up -d
	docker-compose -p pipeline ps

down:
	docker-compose -p pipeline down --remove-orphans

all-tests: down build test-up

logs:
	docker-compose -p pipeline logs $(SERVICE)

restart:
	docker-compose -p pipeline restart $(SERVICE)