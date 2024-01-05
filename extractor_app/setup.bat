@echo off
python -m venv .venv
.\.venv\Scripts\pip.exe install pydicom
.\.venv\Scripts\pip.exe install pandas