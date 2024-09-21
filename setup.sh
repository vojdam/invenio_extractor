#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
python3 -m flask --app extractor_app init-db
python3 -m flask --app extractor_app update-db -r True
