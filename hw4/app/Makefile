APP = api

init:
	python3 -m venv venv
	source venv/bin/activate
    pip3 install python-dotenv fastapi uvicorn loguru python-multipart pytest pytest-asyncio requests httpx

run:
	cd api && python3 -m uvicorn app:APP --reload --host 0.0.0.0

test:
	python3 -m pytest
