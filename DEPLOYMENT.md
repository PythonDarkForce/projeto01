# Production Deployment Guide

This guide will help you deploy the Django Blog application with WebSocket support to a production environment.

## Prerequisites

- Ubuntu/Debian server (or similar Linux distribution)
- Python 3.8 or higher
- Redis server
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)

## Step 1: Server Setup

### Update system packages
```bash
sudo apt update
sudo apt upgrade -y
```

### Install required packages
```bash
sudo apt install -y python3-pip python3-venv nginx redis-server supervisor
```

### Start and enable Redis
```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## Step 2: Application Setup

### Create application user
```bash
sudo adduser --system --group --home /opt/mysite mysite
```

### Clone repository
```bash
sudo -u mysite git clone <your-repo-url> /opt/mysite/app
cd /opt/mysite/app
```

### Create virtual environment
```bash
sudo -u mysite python3 -m venv /opt/mysite/venv
```

### Install dependencies
```bash
sudo -u mysite /opt/mysite/venv/bin/pip install -r requeriments.txt
```

## Step 3: Configuration

### Create .env file
```bash
sudo -u mysite nano /opt/mysite/app/.env
```

Add the following configuration:
```env
SECRET_KEY=<generate-a-secure-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
REDIS_URL=redis://localhost:6379/0
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

To generate a secure SECRET_KEY:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Run migrations
```bash
cd /opt/mysite/app/mysite
sudo -u mysite /opt/mysite/venv/bin/python manage.py migrate
```

### Create superuser
```bash
sudo -u mysite /opt/mysite/venv/bin/python manage.py createsuperuser
```

### Collect static files
```bash
sudo -u mysite /opt/mysite/venv/bin/python manage.py collectstatic --noinput
```

## Step 4: Supervisor Configuration

Supervisor will manage the Daphne ASGI server process.

### Create supervisor configuration
```bash
sudo nano /etc/supervisor/conf.d/mysite.conf
```

Add the following:
```ini
[program:mysite]
command=/opt/mysite/venv/bin/daphne -u /tmp/mysite.sock mysite.asgi:application
directory=/opt/mysite/app/mysite
user=mysite
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/mysite.log
environment=DJANGO_SETTINGS_MODULE="mysite.settings"
```

### Update supervisor
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mysite
```

### Check status
```bash
sudo supervisorctl status mysite
```

## Step 5: Nginx Configuration

Nginx will act as a reverse proxy for both HTTP and WebSocket connections.

### Create Nginx configuration
```bash
sudo nano /etc/nginx/sites-available/mysite
```

Add the following:
```nginx
upstream mysite {
    server unix:/tmp/mysite.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 4G;

    access_log /var/log/nginx/mysite-access.log;
    error_log /var/log/nginx/mysite-error.log;

    location /static/ {
        alias /opt/mysite/app/mysite/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /ws/ {
        proxy_pass http://mysite;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://mysite;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable site
```bash
sudo ln -s /etc/nginx/sites-available/mysite /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 6: SSL Certificate (Let's Encrypt)

### Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtain certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Auto-renewal
Certbot automatically sets up renewal. Verify with:
```bash
sudo certbot renew --dry-run
```

## Step 7: Firewall Configuration

### Configure UFW
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Step 8: Monitoring and Maintenance

### View application logs
```bash
sudo tail -f /var/log/mysite.log
```

### View Nginx logs
```bash
sudo tail -f /var/log/nginx/mysite-access.log
sudo tail -f /var/log/nginx/mysite-error.log
```

### Restart application
```bash
sudo supervisorctl restart mysite
```

### Update application
```bash
cd /opt/mysite/app
sudo -u mysite git pull
sudo -u mysite /opt/mysite/venv/bin/pip install -r requeriments.txt
cd mysite
sudo -u mysite /opt/mysite/venv/bin/python manage.py migrate
sudo -u mysite /opt/mysite/venv/bin/python manage.py collectstatic --noinput
sudo supervisorctl restart mysite
```

## Step 9: Health Checks

### Check Redis
```bash
redis-cli ping
# Should return: PONG
```

### Check Daphne
```bash
sudo supervisorctl status mysite
# Should show: RUNNING
```

### Check Nginx
```bash
sudo systemctl status nginx
# Should show: active (running)
```

### Test WebSocket connection
Visit your site and check the browser console for WebSocket connection messages.

## Troubleshooting

### Application won't start
1. Check logs: `sudo tail -f /var/log/mysite.log`
2. Verify .env file is correct
3. Check Redis is running: `redis-cli ping`
4. Verify permissions: Files should be owned by `mysite` user

### WebSocket not connecting
1. Check Nginx WebSocket configuration
2. Verify SSL certificate is valid
3. Check browser console for errors
4. Verify Redis is running

### Static files not loading
1. Run collectstatic: `sudo -u mysite /opt/mysite/venv/bin/python manage.py collectstatic --noinput`
2. Check Nginx static files location matches configuration
3. Verify permissions on staticfiles directory

## Security Recommendations

1. **Keep software updated**: Regularly update system packages and Python dependencies
2. **Use strong SECRET_KEY**: Never commit SECRET_KEY to version control
3. **Enable firewall**: Only allow necessary ports
4. **Regular backups**: Backup database and media files regularly
5. **Monitor logs**: Set up log monitoring and alerting
6. **Use Redis password**: Configure Redis with authentication
7. **Limit permissions**: Use dedicated user account with minimal permissions
8. **Rate limiting**: Consider adding rate limiting to prevent abuse

## Performance Optimization

1. **Redis connection pooling**: Already configured in channel layers
2. **Static file compression**: Enabled via WhiteNoise
3. **Database optimization**: Consider PostgreSQL for production
4. **Caching**: Add Django caching for frequently accessed data
5. **CDN**: Use CDN for static files
6. **Load balancing**: For high traffic, use multiple Daphne workers

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Channels Deployment](https://channels.readthedocs.io/en/latest/deploying.html)
- [Nginx WebSocket Proxying](https://nginx.org/en/docs/http/websocket.html)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
