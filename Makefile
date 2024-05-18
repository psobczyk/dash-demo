
DOCKER_IMAGE = "uam_dash"

# build docker image
.PHONY:
docker-build:
	docker build -t $(DOCKER_IMAGE) .

docker-run: docker-build
	docker run --rm -p 8000:8000 $(DOCKER_IMAGE)

docker-run-compose: docker-build
	docker-compose build
	docker-compose up

make-requirements: requirements.in
	pip install pip-tools
	pip-compile --generate-hashes requirements.in

venv: requirements.txt
	python3 -m venv .venv
	. .venv/bin/activate; \
	pip install --upgrade virtualenv; \
	pip install --upgrade pip setuptools wheel; \
	pip install -r requirements.txt

clean-venv:
	rm -rf .venv

.PHONY: docker-build
test: 
	docker run --rm $(DOCKER_IMAGE) python -m pytest 

.PHONY: venv
black:
	black src/