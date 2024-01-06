@echo off
python -m venv .venv
.venv\Scripts\pip.exe install pydicom
.venv\Scripts\pip.exe install flask
.venv\Scripts\python.exe -m flask --app extractor_app init-db