# Django Blog with WebSocket Support

A production-ready Django blog application with real-time WebSocket capabilities for live updates.

## Features

- **WebSocket Support**: Real-time updates for blog posts using Django Channels
- **Production-Ready Configuration**: Environment-based settings, security headers, and logging
- **Blog Post Management**: Create, update, and delete blog posts through Django admin
- **Real-time Notifications**: Connected clients receive instant notifications when posts are created, updated, or deleted

## Requirements

- Python 3.8+
- Redis (optional, for production channel layers)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd projeto01
```

2. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requeriments.txt
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Generate a new SECRET_KEY for production:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

6. Update the `.env` file with your configuration:
```env
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

7. Run migrations:
```bash
cd mysite
python3 manage.py migrate
```

8. Create a superuser:
```bash
python3 manage.py createsuperuser
```

9. Collect static files (for production):
```bash
python3 manage.py collectstatic
```

## Development

Run the development server with DEBUG mode:

```bash
cd mysite
DEBUG=True python3 manage.py runserver
```

The application will be available at `http://localhost:8000`

## Production Deployment

### Using Daphne (recommended for WebSocket support)

1. Set up Redis for channel layers:
```bash
# Install Redis if not already installed
sudo apt-get install redis-server
```

2. Update `.env` with Redis URL:
```env
REDIS_URL=redis://localhost:6379/0
```

3. Run Daphne:
```bash
daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
```

### Using Gunicorn (for HTTP only)

For traditional HTTP deployment without WebSocket support:

```bash
gunicorn mysite.wsgi:application --bind 0.0.0.0:8000
```

## WebSocket API

### Connection

Connect to the WebSocket endpoint:
```
ws://your-domain.com/ws/blog/
```

### Ping/Pong

Keep connection alive by sending a ping:
```json
{"type": "ping"}
```

Response:
```json
{"type": "pong"}
```

### Receiving Updates

When a blog post is created, updated, or deleted, all connected clients receive:

```json
{
    "type": "blog_update",
    "action": "create|update|delete",
    "post": {
        "id": 1,
        "title": "Post Title",
        "author": "username",
        "created_date": "2025-10-22",
        "published_date": "2025-10-22"
    }
}
```

## Testing

Run the test suite:

```bash
cd mysite
python3 manage.py test
```

## Security

This application includes production-ready security features:

- Environment-based SECRET_KEY management
- DEBUG mode disabled by default
- HTTPS enforcement (SECURE_SSL_REDIRECT)
- Secure cookies (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
- Security headers (XSS protection, content type sniffing protection)
- HSTS headers for HTTPS enforcement
- Static file compression and caching with WhiteNoise

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Django secret key | (required for production) |
| DEBUG | Enable debug mode | False |
| ALLOWED_HOSTS | Comma-separated list of allowed hosts | 127.0.0.1,localhost |
| REDIS_URL | Redis URL for channel layers | (optional, uses in-memory in dev) |
| SECURE_SSL_REDIRECT | Redirect HTTP to HTTPS | True (in production) |
| SESSION_COOKIE_SECURE | Use secure session cookies | True (in production) |
| CSRF_COOKIE_SECURE | Use secure CSRF cookies | True (in production) |

## Project Structure

```
projeto01/
├── mysite/
│   ├── blog/
│   │   ├── consumers.py       # WebSocket consumers
│   │   ├── routing.py         # WebSocket URL routing
│   │   ├── utils.py           # Utility functions for notifications
│   │   ├── models.py          # Blog post models
│   │   ├── admin.py           # Admin configuration
│   │   ├── tests.py           # Test cases
│   │   └── views.py           # HTTP views
│   ├── mysite/
│   │   ├── settings.py        # Django settings (production-ready)
│   │   ├── urls.py            # URL configuration
│   │   ├── asgi.py            # ASGI configuration for WebSockets
│   │   └── wsgi.py            # WSGI configuration
│   └── manage.py
├── requeriments.txt           # Python dependencies
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## License

This project is open source and available under the MIT License.
