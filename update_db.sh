#!/bin/bash

source .venv/bin/activate
python3 -m flask --app extractor_app update-db
