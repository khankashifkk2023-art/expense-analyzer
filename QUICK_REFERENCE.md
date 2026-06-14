# SplitLedger — Quick Reference Card

One-page reference for common tasks and commands.

---

## 🚀 Quick Start (First Time)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file (copy from .env.example)
# Edit with your MySQL credentials

# 3. Create database in MySQL
mysql -u root -p -e "CREATE DATABASE splitledger CHARACTER SET utf8mb4;"

# 4. Run setup script
python setup.py

# 5. Start server
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## 📋 Common Management Commands

```bash
# Database
python manage.py makemigrations      # Create migrations
python manage.py migrate             # Apply migrations
python manage.py dbshell             # Open database shell

# Users
python manage.py createsuperuser     # Create admin
python manage.py changepassword user # Change password

# Server
python manage.py runserver           # Development server
python manage.py runserver 0.0.0.0:8000  # All interfaces

# Static Files
python manage.py collectstatic       # Collect static files

# Shell
python manage.py shell               # Django shell
```

---

## 🔐 Test Credentials (After setup.py)

| Username | Password | Role |
|----------|----------|------|
| john | password123 | Member |
| jane | password123 | Member |
| mike | password123 | Member |

**Admin:** Create with `python manage.py createsuperuser`

---

## 🌐 URL Reference

| URL | Purpose |
|-----|---------|
| `/` | Home / Group list |
| `/auth/register/` | User registration |
| `/auth/login/` | User login |
| `/auth/logout/` | User logout |
| `/admin/` | Admin panel |
| `/groups/` | Group list |
| `/groups/create/` | Create group |
| `/groups/<id>/` | Group detail |
| `/groups/<id>/expenses/` | Expense list |
| `/groups/<id>/balances/` | Balance view |
| `/groups/<id>/settlements/` | Settlement list |
| `/groups/<id>/import/` | CSV import |

---

## 💾 Database Quick Reference

### Create Backup
```bash
mysqldump -u root -p splitledger > backup.sql
```

### Restore Backup
```bash
mysql -u root -p splitledger < backup.sql
```

### Reset Database
```bash
python manage.py flush              # Clear all data
python manage.py migrate            # Reapply migrations
python setup.py                     # Recreate sample data
```

---

## 📁 CSV Import Format

```csv
date,description,amount,currency,paid_by,split_type,notes
2026-06-01,Groceries,1500.00,INR,john,equal,Weekly shopping
2026-06-02,Electricity,850.50,INR,jane,equal,May bill
```

**Required Fields:**
- `date` (YYYY-MM-DD)
- `description`
- `amount` (decimal)
- `currency` (INR or USD)
- `paid_by` (username)

**Optional Fields:**
- `split_type` (default: equal)
- `notes`

---

## 🔧 Configuration (.env)

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

DB_NAME=splitledger
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=3306

USD_TO_INR_RATE=83.50
```

---

## 🐛 Troubleshooting Quick Fixes

### Can't connect to database
```bash
# Check MySQL is running
mysql -u root -p

# Verify credentials in .env
# Check database exists
mysql -u root -p -e "SHOW DATABASES;"
```

### ModuleNotFoundError
```bash
pip install -r requirements.txt --upgrade
```

### Migration errors
```bash
# Delete migrations (except __init__.py)
rm core/migrations/0*.py

# Recreate
python manage.py makemigrations
python manage.py migrate
```

### Static files not loading
```bash
python manage.py collectstatic
# Check STATIC_URL in settings.py
```

### Port already in use
```bash
# Use different port
python manage.py runserver 8080

# Or kill existing process
# Windows: netstat -ano | findstr :8000
#          taskkill /PID <PID> /F
```

---

## 📊 Sample Data Creation

```python
# In Django shell: python manage.py shell

from django.contrib.auth.models import User
from core.models import ExpenseGroup, GroupMembership
from datetime import date

# Create user
user = User.objects.create_user('testuser', 'test@test.com', 'password123')

# Create group
group = ExpenseGroup.objects.create(name='Test Group', created_by=user)

# Add member
GroupMembership.objects.create(group=group, user=user, date_joined=date.today())
```

---

## 🎨 Theme Colors (CSS Variables)

| Color | Variable | Hex |
|-------|----------|-----|
| Primary | `--primary` | `#6c63ff` |
| Success | `--success` | `#00d4aa` |
| Danger | `--danger` | `#ff6b6b` |
| Warning | `--warning` | `#ffd93d` |
| Background | `--bg-primary` | `#0a0a1a` |
| Text | `--text-primary` | `#e8e8f0` |

---

## 🔍 Useful Django Shell Commands

```python
# Get all users
from django.contrib.auth.models import User
User.objects.all()

# Get all groups
from core.models import ExpenseGroup
ExpenseGroup.objects.all()

# Get expenses for a group
from core.models import Expense
Expense.objects.filter(group_id=1)

# Calculate total expenses
from django.db.models import Sum
Expense.objects.aggregate(Sum('amount_inr'))
```

---

## 📈 Performance Monitoring

```python
# In settings.py, enable query logging
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

---

## 🔒 Security Checklist (Production)

- [ ] `DEBUG=False`
- [ ] Change `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS`
- [ ] Use HTTPS
- [ ] Strong database password
- [ ] Regular backups
- [ ] Update dependencies
- [ ] Monitor logs

---

## 📦 Project Structure (Quick View)

```
expense/
├── manage.py              # CLI tool
├── requirements.txt       # Dependencies
├── .env                   # Configuration
├── splitledger/           # Project settings
├── core/                  # Main app
│   ├── models.py          # 7 models
│   ├── views/             # 6 modules
│   ├── forms.py           # 8 forms
│   └── urls.py            # 24 routes
├── templates/             # 20+ HTML files
└── static/                # CSS & JS
```

---

## 💡 Tips & Tricks

### View SQL Queries
```python
from django.db import connection
print(connection.queries)
```

### Reset Admin Password
```bash
python manage.py changepassword admin
```

### Clear All Data
```bash
python manage.py flush
```

### Create Migration Without Applying
```bash
python manage.py makemigrations --dry-run
```

### Check for Issues
```bash
python manage.py check
python manage.py check --deploy  # Production checks
```

---

## 📞 Need Help?

1. **README.md** — Complete documentation
2. **QUICKSTART.md** — Setup guide
3. **TECH.md** — Technical details
4. **Django Docs** — https://docs.djangoproject.com/
5. **Stack Overflow** — Tag: django

---

## 🎯 Common Tasks

### Add New User via Admin
1. Go to http://127.0.0.1:8000/admin/
2. Auth → Users → Add user
3. Fill in details and save

### Export Data
```bash
python manage.py dumpdata core > data.json
```

### Import Data
```bash
python manage.py loaddata data.json
```

### Test Email (Console Backend)
```python
# In settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

**Quick Reference v1.0 — June 14, 2026**
