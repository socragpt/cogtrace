PYTHON ?= python3
export PYTHONPATH := src

.PHONY: test fixture check status

test:
	$(PYTHON) -m unittest discover -s tests -v

fixture:
	$(PYTHON) -m cogtrace pilot examples/pilot-tasks.json \
		--backend fixture \
		--output runs/fixture-pilot.jsonl

check: test fixture

status:
	git status --short --branch
	git log -3 --oneline --decorate
