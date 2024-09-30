NETWORK?=backend-web-1  

build:
	cp ../../dissemination/sql/sling/public_data_v1_0_0/public_data_v1_0_0.yaml data/sling.yaml
	docker build -t facloaddata .

run:
	docker run -i --rm -v ${PWD}:/app --network container:${NETWORK} -t facloaddata
