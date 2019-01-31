
SHELL = /bin/bash

build:
	docker build --tag bench:latest .

build-wheels:
	docker build -f Dockerfile.wheels --tag bench:latest .


shell:
	docker build --tag bench:latest .
	docker run --name docker  \
		--volume $(shell pwd)/:/local \
		--rm -it bench:latest bash

test-wheel: build-wheels
	docker run \
		--name bench \
		-w /local/scripts \
		--volume $(shell pwd)/:/local \
		--env VSI_CACHE=FALSE \
		--env VSI_CACHE_SIZE=0 \
		--env GDAL_CACHEMAX=0 \
		-itd \
		bench:latest bash
	docker exec -it bench bash -c 'python test_1b_colormap.py'
	docker exec -it bench bash -c 'python test_1b.py'
	docker exec -it bench bash -c 'python test_3b.py'
	docker stop bench
	docker rm bench

test: build
	docker run \
		--name bench \
		-w /local/scripts \
		--volume $(shell pwd)/:/local \
		--env VSI_CACHE=FALSE \
		--env VSI_CACHE_SIZE=0 \
		--env GDAL_CACHEMAX=0 \
		-itd \
		bench:latest bash
	docker exec -it bench bash -c 'python test_1b_colormap.py'
	docker exec -it bench bash -c 'python test_1b.py'
	docker exec -it bench bash -c 'python test_3b.py'
	docker stop bench
	docker rm bench

clean:
	docker stop bench
	docker rm bench
