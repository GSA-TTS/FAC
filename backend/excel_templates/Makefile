VENV           = .venv
VENV_PYTHON    = $(VENV)/bin/python
SYSTEM_PYTHON  = $(or $(shell which python3), $(shell which python))
PYTHON         = $(or $(wildcard $(VENV_PYTHON)), $(SYSTEM_PYTHON))

$(VENV_PYTHON):
	rm -rf $(VENV)
	$(SYSTEM_PYTHON) -m venv $(VENV)

venv: $(VENV_PYTHON)

deps:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

.PHONY: venv deps

specs = $(wildcard definitions/*.jsonnet)
# xlsx = $(patsubst definitions/%.jsonnet,%.xlsx,$(wildcard definitions/*.jsonnet))
xlsx = $(wildcard *-template-*.xlsx)

all:
	for f in $(specs); do \
		python3 render.py $$f; \
	done

clean:
	for f in $(xlsx); do \
		rm $$f; \
	done