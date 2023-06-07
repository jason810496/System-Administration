APP = api

run:
	. venv/bin/activate
	cd api && python3 -m uvicorn app:APP --reload --host 0.0.0.0

test:
	python3 -m pytest
