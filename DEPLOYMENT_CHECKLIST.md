# SplitLedger — Deployment Checklist

Use this checklist to deploy SplitLedger to production.

## Pre-Deployment Checklist

### 1. Code Review ✅
- [ ] All views have proper authentication decorators
- [ ] Forms have CSRF protection
- [ ] SQL queries use ORM (no raw SQL)
- [ ] User inputs are validated
- [ ] Error handling is implemented
- [ ] Logging is configured

### 2. Security Configuration 🔒

#### Environment Variables
- [ ] Generate new `SECRET_KEY` (never use development key)
  ```bash
  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
  ```
- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure `ALLOWED_HOSTS` with production domains
  ```python
  ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
  ```
- [ ] Set strong database password
- [ ] Configure proper USD_TO_INR_RATE or API

#### Django Security Settings
Add to `settings.py`:
```python
# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 3. Database Setup 🗄️

#### MySQL Production Configuration
- [ ] Create production database
  ```sql
  CREATE DATABASE splitledger_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```
- [ ] Create dedicated database user
  ```sql
  CREATE USER 'splitledger_user'@'localhost' IDENTIFIED BY 'strong_password';
  GRANT ALL PRIVILEGES ON splitledger_prod.* TO 'splitledger_user'@'localhost';
  FLUSH PRIVILEGES;
  ```
- [ ] Update `.env` with production credentials
- [ ] Run migrations
  ```bash
  python manage.py migrate
  ```
- [ ] Create superuser
  ```bash
  python manage.py createsuperuser
  ```

#### Database Backup Strategy
- [ ] Set up automated daily backups
  ```bash
  mysqldump -u user -p splitledger_prod > backup_$(date +%Y%m%d).sql
  ```
- [ ] Test backup restoration
- [ ] Store backups off-site (S3, separate server)

### 4. Static Files 📦

#### Collect Static Files
- [ ] Set `STATIC_ROOT` in settings.py
  ```python
  STATIC_ROOT = BASE_DIR / 'staticfiles'
  ```
- [ ] Run collectstatic
  ```bash
  python manage.py collectstatic --noinput
  ```
- [ ] Configure nginx to serve static files directly

#### Media Files
- [ ] Set up media directory with proper permissions
  ```bash
  mkdir -p /var/www/splitledger/media
  chown -R www-data:www-data /var/www/splitledger/media
  ```
- [ ] Configure nginx to serve media files
- [ ] Consider S3/CDN for media storage (optional)

### 5. Web Server Configuration 🌐

#### Install nginx
```bash
sudo apt update
sudo apt install nginx
```

#### nginx Configuration
Create `/etc/nginx/sites-available/splitledger`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Static files
    location /static/ {
        alias /var/www/splitledger/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/splitledger/media/;
        expires 30d;
    }
    
    # Proxy to gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/splitledger /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. WSGI Server Setup ⚙️

#### Install gunicorn
```bash
pip install gunicorn
```

#### Create gunicorn service
Create `/etc/systemd/system/splitledger.service`:
```ini
[Unit]
Description=SplitLedger gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/splitledger
Environment="PATH=/var/www/splitledger/venv/bin"
ExecStart=/var/www/splitledger/venv/bin/gunicorn \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          --access-logfile /var/log/splitledger/access.log \
          --error-logfile /var/log/splitledger/error.log \
          splitledger.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start splitledger
sudo systemctl enable splitledger
sudo systemctl status splitledger
```

### 7. SSL/TLS Configuration 🔐

#### Install Certbot (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
```

#### Obtain SSL Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### Auto-renewal
```bash
sudo certbot renew --dry-run
```

### 8. Logging & Monitoring 📊

#### Configure Django Logging
Add to `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/splitledger/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

#### Create Log Directory
```bash
sudo mkdir -p /var/log/splitledger
sudo chown -R www-data:www-data /var/log/splitledger
```

#### Set Up Log Rotation
Create `/etc/logrotate.d/splitledger`:
```
/var/log/splitledger/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

#### Optional: Monitoring Tools
- [ ] Install and configure Sentry for error tracking
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure server monitoring (New Relic, Datadog)

### 9. Performance Optimization ⚡

#### Database
- [ ] Add database indexes for frequently queried fields
- [ ] Enable query optimization
- [ ] Set up connection pooling

#### Caching (Optional)
Install Redis:
```bash
sudo apt install redis-server
pip install django-redis
```

Configure in `settings.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

#### Static Files
- [ ] Enable gzip compression in nginx
- [ ] Set proper cache headers
- [ ] Consider CDN (CloudFlare, AWS CloudFront)

### 10. Email Configuration 📧

For password reset and notifications:

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
```

### 11. Firewall Configuration 🛡️

```bash
# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### 12. Final Checks ✅

#### Security
- [ ] Run Django security check
  ```bash
  python manage.py check --deploy
  ```
- [ ] Test all forms for CSRF protection
- [ ] Verify file upload restrictions
- [ ] Test authentication and authorization
- [ ] Run security scanner (OWASP ZAP, Burp Suite)

#### Functionality
- [ ] User registration and login
- [ ] Create and manage groups
- [ ] Add and edit expenses
- [ ] View balances
- [ ] Record settlements
- [ ] CSV import
- [ ] Admin panel access
- [ ] Password reset (if configured)

#### Performance
- [ ] Test page load times
- [ ] Check database query performance
- [ ] Verify static files load correctly
- [ ] Test under load (Apache Bench, LoadRunner)

#### Backups
- [ ] Test database backup
- [ ] Test database restore
- [ ] Verify media files backup
- [ ] Document backup procedure

#### Documentation
- [ ] Update deployment documentation
- [ ] Document server credentials (securely)
- [ ] Create runbook for common issues
- [ ] Document backup/restore procedures

## Post-Deployment

### 1. Monitoring Setup
- [ ] Configure uptime monitoring
- [ ] Set up error alerting
- [ ] Monitor disk space
- [ ] Monitor database performance

### 2. Maintenance Plan
- [ ] Schedule regular updates
- [ ] Plan security audits
- [ ] Set backup verification schedule
- [ ] Document incident response procedures

### 3. User Training
- [ ] Prepare user documentation
- [ ] Create video tutorials (optional)
- [ ] Set up support channel

## Emergency Procedures

### Rollback Plan
1. Stop gunicorn service
   ```bash
   sudo systemctl stop splitledger
   ```
2. Restore database backup
   ```bash
   mysql -u user -p splitledger_prod < backup_YYYYMMDD.sql
   ```
3. Restore previous code version
4. Restart services
   ```bash
   sudo systemctl start splitledger
   ```

### Common Issues

**502 Bad Gateway**
- Check gunicorn is running: `sudo systemctl status splitledger`
- Check logs: `sudo tail -f /var/log/splitledger/error.log`

**500 Internal Server Error**
- Check Django logs: `sudo tail -f /var/log/splitledger/django.log`
- Verify database connection
- Check permissions on media directory

**Static Files Not Loading**
- Run collectstatic again
- Check nginx static file configuration
- Verify file permissions

## Maintenance Checklist (Monthly)

- [ ] Review error logs
- [ ] Update dependencies
  ```bash
  pip install --upgrade -r requirements.txt
  ```
- [ ] Run security updates
  ```bash
  sudo apt update && sudo apt upgrade
  ```
- [ ] Test backup restoration
- [ ] Review disk usage
- [ ] Check SSL certificate expiry
- [ ] Review access logs for suspicious activity

## Support Contacts

- **Server Provider:** _____________
- **Domain Registrar:** _____________
- **SSL Provider:** Let's Encrypt
- **Database Admin:** _____________
- **System Admin:** _____________

---

**Deployment Date:** _______________  
**Deployed By:** _______________  
**Version:** 1.0.0  
**Last Updated:** June 14, 2026
