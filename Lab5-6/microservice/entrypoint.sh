#!/bin/sh

sleep 15
pipenv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
