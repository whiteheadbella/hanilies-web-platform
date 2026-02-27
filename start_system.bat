@echo off
setlocal

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
  echo [ERROR] Virtual environment not found at venv\Scripts\activate.bat
  echo Create it first with: python -m venv venv
  pause
  exit /b 1
)

call "venv\Scripts\activate.bat"

echo Running migrations...
python manage.py migrate
if errorlevel 1 (
  echo [ERROR] Migration failed.
  pause
  exit /b 1
)

echo Starting Django server at http://127.0.0.1:8000/
start "" http://127.0.0.1:8000/
python manage.py runserver 127.0.0.1:8000

endlocal
