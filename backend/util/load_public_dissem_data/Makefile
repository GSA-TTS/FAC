NETWORK?=backend-web-1  

build:
	docker build -t facloaddata .

run:
	docker run -i --rm -v ${PWD}:/app --network container:${NETWORK} -t facloaddata
