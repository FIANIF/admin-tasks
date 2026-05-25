@echo off
REM Admin Tasks System Setup for Windows

echo 🚀 Starting Admin Tasks System Setup...

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from .env.example...
    copy .env.example .env
    echo ✏️  Please edit .env with your configuration
    exit /b 1
)

REM Create virtual environment
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Run migrations
echo 🗄️  Running migrations...
python manage.py migrate

REM Collect static files
echo 📦 Collecting static files...
python manage.py collectstatic --noinput

echo.
echo ✅ Setup complete!
echo.
echo 🎯 Next steps:
echo 1. Run in Terminal 1: python manage.py runserver
echo 2. Run in Terminal 2: celery -A admin_tasks worker -l info
echo 3. Run in Terminal 3: celery -A admin_tasks beat -l info
echo.
echo 🌐 Access:
echo    Admin Panel: http://localhost:8000/admin/
echo    API: http://localhost:8000/api/tasks/
echo.
echo 📧 Configure email in .env before tasks will send notifications
echo.
pause
