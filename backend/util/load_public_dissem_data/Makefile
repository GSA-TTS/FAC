NETWORK?=backend-db2-1

build:
	docker build -t facloaddata --build-arg FAC_DB_URI=${FAC_DB_URI} .

run:
	docker run -i --rm -v ${PWD}:/app --network container:${NETWORK} -t facloaddata

run_remote:
	docker run -i --rm -v ${PWD}:/app facloaddata "${FAC_DB_URI}"
