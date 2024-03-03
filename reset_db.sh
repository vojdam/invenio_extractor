#!/bin/bash

source .venv/bin/activate
python3 -m flask --app extractor_app init-db
python3 -m flask --app extractor_app update-db