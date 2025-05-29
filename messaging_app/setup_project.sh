#!/bin/bash

# Django Messaging App Setup Script
echo "Setting up Django Messaging Application..."

# Create virtual environment
echo "Creating virtual environment..."
python -m venv messaging_env

# Activate virtual environment
echo "Activating virtual environment..."
source messaging_env/bin/activate  # On Windows: messaging_env\Scripts\activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create Django project structure
echo "Creating Django project..."
django-admin startproject messaging_app .

# Create chats app
echo "Creating chats app..."
cd messaging_app
python manage.py startapp chats

# Run migrations
echo "Creating and applying migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
echo "Creating superuser..."
python manage.py createsuperuser

# Run development server
echo "Starting development server..."
python manage.py runserver

echo "Setup complete! Your Django messaging app is ready."
echo "Visit http://127.0.0.1:8000/api/ to access the API"
echo "Visit http://127.0.0.1:8000/admin/ to access the admin panel"