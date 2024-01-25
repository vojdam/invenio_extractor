@echo off
explorer "http://127.0.0.1:5000"
.venv\Scripts\python.exe -m flask --app extractor_app run --debug
pause