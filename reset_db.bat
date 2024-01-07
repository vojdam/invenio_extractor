@echo off
.venv\Scripts\python.exe -m flask --app extractor_app init-db
.venv\Scripts\python.exe -m flask --app extractor_app update-db
pause