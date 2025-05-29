# Django Messaging API

A robust RESTful API for a messaging application built with Django and Django REST Framework.

## Features

- **User Management**: Custom user model with extended profile information
- **Conversations**: Multi-participant conversation support
- **Messages**: Real-time messaging within conversations
- **RESTful API**: Clean, well-documented API endpoints
- **Admin Interface**: Django admin for easy data management
- **Authentication**: Built-in authentication and permissions

## Project Structure

\`\`\`
messaging_app/
├── messaging_app/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── chats/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── manage.py
├── requirements.txt
└── README.md
\`\`\`

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd messaging_app