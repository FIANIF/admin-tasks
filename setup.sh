#!/bin/bash

echo "🚀 Starting Admin Tasks System..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit .env with your configuration"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️  Running migrations..."
python manage.py migrate

# Create superuser if doesn't exist
echo "👤 Creating superuser (press Ctrl+C if already exists)..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com 2>/dev/null || true

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Run in Terminal 1: python manage.py runserver"
echo "2. Run in Terminal 2: celery -A admin_tasks worker -l info"
echo "3. Run in Terminal 3: celery -A admin_tasks beat -l info"
echo ""
echo "🌐 Access:"
echo "   Admin Panel: http://localhost:8000/admin/"
echo "   API: http://localhost:8000/api/tasks/"
echo ""
echo "📧 Configure email in .env before tasks will send notifications"
echo ""
