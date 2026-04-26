@echo off
setlocal enabledelayedexpansion
if not exist venv (
  python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt
if not exist colleges.db (
  echo Colleges database not found. Run seed_colleges.py if needed before starting.
)
python app.py
