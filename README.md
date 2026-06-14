# SplitLedger — Shared Expense Tracker

A modern, full-featured Django application for tracking shared expenses among groups. Perfect for flatmates, travel groups, or any situation where people share costs.

![Tech Stack](https://img.shields.io/badge/Django-6.0-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange)

## ✨ Features

### Core Functionality
- **👥 Group Management** — Create unlimited expense groups with time-bounded memberships
- **💸 Multi-Currency Support** — Track expenses in INR and USD with automatic conversion
- **🎯 Flexible Expense Splitting** — Four split types:
  - Equal split (divide evenly)
  - Exact amounts (specify per person)
  - Percentage-based (weighted distribution)
  - Share/ratio-based (proportional split)
- **⚖️ Real-Time Balance Calculation** — Automatic debt tracking between members
- **💰 Smart Settlement Suggestions** — Minimize transactions needed to settle all debts
- **📊 Detailed Balance Breakdown** — See exactly who paid what and who owes what
- **📁 CSV Bulk Import** — Import expenses in bulk with intelligent anomaly detection
- **🔍 Audit Trail** — Full history of conversions, splits, and import sessions

### User Experience
- **🎨 Beautiful Dark UI** — Modern glassmorphism design with vibrant accents
- **📱 Fully Responsive** — Works seamlessly on desktop, tablet, and mobile
- **⚡ Fast & Lightweight** — No heavy frontend frameworks, pure vanilla JS
- **🔐 Secure Authentication** — Django's battle-tested auth system
- **💬 Smart Notifications** — Flash messages for all important actions

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository** (or download the files)
```bash
cd c:\Users\afaqu\OneDrive\Desktop\expense
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Update database credentials and secret key:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=splitledger
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_HOST=127.0.0.1
DB_PORT=3306
USD_TO_INR_RATE=83.50
```

5. **Create MySQL database**
```sql
CREATE DATABASE splitledger CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Create a superuser** (for admin access)
```bash
python manage.py createsuperuser
```

8. **Run the development server**
```bash
python manage.py runserver
```

9. **Access the application**
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 📖 Usage Guide

### Getting Started

1. **Register an account** at `/auth/register/`
2. **Create your first group** — Click "Create Group" on the dashboard
3. **Add members** — Invite users to join your group
4. **Add expenses** — Record who paid for what
5. **View balances** — See who owes whom in real-time
6. **Settle up** — Record payments between members

### Expense Splitting Examples

#### Equal Split
```
Expense: Groceries — ₹1,200
Split among: 4 people
Each person owes: ₹300
```

#### Percentage Split
```
Expense: Rent — ₹30,000
Person A: 40% → ₹12,000
Person B: 30% → ₹9,000
Person C: 30% → ₹9,000
```

#### Exact Amounts
```
Expense: Restaurant Bill — ₹2,500
Person A ordered: ₹800
Person B ordered: ₹1,200
Person C ordered: ₹500
```

#### Share-Based Split
```
Expense: Hotel Room — ₹6,000
Couple (2 shares): ₹4,000
Single (1 share): ₹2,000
```

### CSV Import

Import bulk expenses using a CSV file with this format:

```csv
date,description,amount,currency,paid_by,split_type,notes
2026-06-01,Groceries,1500.00,INR,john,equal,Weekly shopping
2026-06-02,Electricity Bill,850.50,INR,jane,equal,May 2026
2026-06-03,Dinner,45.00,USD,john,equal,Pizza night
```

The system automatically detects 15+ types of anomalies including:
- Duplicate entries
- Missing fields
- Invalid amounts or currencies
- Unknown members
- Date format issues
- And more...

## 🏗️ Project Structure

```
splitledger/
├── splitledger/              # Main project configuration
│   ├── settings.py           # Django settings
│   ├── urls.py               # Root URL configuration
│   ├── wsgi.py               # WSGI entry point
│   └── asgi.py               # ASGI entry point (async)
│
├── core/                     # Main application
│   ├── models.py             # Database models (7 models)
│   ├── views/                # View logic (organized by feature)
│   │   ├── auth_views.py     # Registration, login, logout
│   │   ├── group_views.py    # Group & membership management
│   │   ├── expense_views.py  # Expense CRUD operations
│   │   ├── balance_views.py  # Balance calculations
│   │   ├── settlement_views.py # Settlement tracking
│   │   └── csv_import_views.py # CSV import workflow
│   ├── forms.py              # Django forms (8 forms)
│   ├── urls.py               # App URL routing
│   ├── admin.py              # Admin interface config
│   ├── services/             # Business logic
│   │   └── csv_import/       # CSV parsing & validation
│   ├── templatetags/         # Custom template filters
│   │   └── core_filters.py   # Currency & balance formatting
│   └── migrations/           # Database migrations
│
├── templates/                # HTML templates
│   ├── base.html             # Base template with nav/footer
│   └── core/                 # Feature-specific templates
│       ├── auth/             # Login, register
│       ├── groups/           # Group management
│       ├── expenses/         # Expense CRUD
│       ├── balances/         # Balance views
│       ├── settlements/      # Settlement management
│       └── csv_import/       # CSV import workflow
│
├── static/                   # Static assets
│   ├── css/style.css         # Complete design system (800+ lines)
│   └── js/main.js            # Vanilla JS utilities
│
├── media/                    # User uploads (CSV files)
├── manage.py                 # Django CLI tool
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── .env.example              # Environment template
├── README.md                 # This file
└── TECH.md                   # Complete tech stack documentation
```

## 🗃️ Database Schema

### Core Tables

- **expense_groups** — Groups of people sharing expenses
- **group_members** — Time-bounded memberships (join/leave dates)
- **expenses** — Individual expenses with currency conversion
- **expense_splits** — Resolved per-user share (always in INR)
- **settlements** — Direct payments between members
- **import_sessions** — CSV import tracking
- **import_anomalies** — Flagged issues during import

### Key Relationships

```
ExpenseGroup (1) ──< (N) GroupMembership ──> (1) User
ExpenseGroup (1) ──< (N) Expense ──> (1) User (paid_by)
Expense (1) ──< (N) ExpenseSplit ──> (1) User
ExpenseGroup (1) ──< (N) Settlement
```

## 🎨 Design System

### Color Palette

| Purpose | Color | Usage |
|---------|-------|-------|
| Primary | `#6c63ff` (Indigo) | Buttons, links, accents |
| Success | `#00d4aa` (Mint) | Positive balances, success messages |
| Danger | `#ff6b6b` (Coral) | Negative balances, delete actions |
| Warning | `#ffd93d` (Amber) | Anomaly flags, warnings |
| Background | `#0a0a1a → #12122a` | Deep space gradient |

### Typography

- **Font:** Inter (Google Fonts)
- **Weights:** 300, 400, 500, 600, 700
- **Scale:** Modular scale from 0.75rem to 2.5rem

### Components

- Glassmorphic cards with backdrop blur
- Custom-styled forms with focus states
- Responsive tables with hover effects
- Badge system for status indicators
- Toast notifications with auto-dismiss
- Empty states with illustrations

## 🔒 Security Features

- ✅ CSRF protection on all forms
- ✅ SQL injection prevention (ORM parameterized queries)
- ✅ Password hashing (Django's PBKDF2)
- ✅ Environment variable secrets
- ✅ Secure session management
- ✅ XSS protection (template auto-escaping)
- ✅ User authentication required for all expense operations

## 📊 Admin Interface

Access the Django admin at `/admin/` to:
- Manage users and permissions
- View all groups, expenses, and settlements
- Inspect expense splits and calculations
- Review CSV import sessions and anomalies
- Monitor system activity

## 🧪 Testing

### Manual Testing Checklist

- [ ] User registration and login
- [ ] Create and manage groups
- [ ] Add and remove members
- [ ] Create expenses with different split types
- [ ] View balance calculations
- [ ] Record settlements
- [ ] Import CSV with clean and flagged data
- [ ] Edit and delete expenses
- [ ] Responsive design on mobile

### Test Data

Use the admin interface or Django shell to create test data:

```python
python manage.py shell

from django.contrib.auth.models import User
from core.models import ExpenseGroup, GroupMembership
from datetime import date

# Create test users
user1 = User.objects.create_user('john', 'john@test.com', 'password123')
user2 = User.objects.create_user('jane', 'jane@test.com', 'password123')

# Create a group
group = ExpenseGroup.objects.create(name='Test Apartment', created_by=user1)

# Add members
GroupMembership.objects.create(group=group, user=user1, date_joined=date.today())
GroupMembership.objects.create(group=group, user=user2, date_joined=date.today())
```

## 🐛 Troubleshooting

### Database Connection Issues

**Error:** `Can't connect to MySQL server`

**Solution:**
1. Ensure MySQL is running
2. Check database credentials in `.env`
3. Verify database exists: `SHOW DATABASES;`
4. Check MySQL is listening on port 3306

### Static Files Not Loading

**Solution:**
```bash
python manage.py collectstatic
```

### Migration Errors

**Solution:**
```bash
# Reset migrations (development only!)
python manage.py migrate --fake core zero
python manage.py migrate
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up proper database (MySQL/PostgreSQL)
- [ ] Configure static file serving (nginx/whitenoise)
- [ ] Set up media file storage (S3/local with nginx)
- [ ] Enable HTTPS
- [ ] Configure email backend (for password reset)
- [ ] Set up logging
- [ ] Configure backup strategy

### Recommended Stack

- **Web Server:** nginx
- **WSGI Server:** gunicorn
- **Database:** MySQL 8.0+ or PostgreSQL 14+
- **Cache:** Redis (optional)
- **Task Queue:** Celery (optional, for async imports)

## 📝 API Endpoints

All endpoints are under the `core` namespace:

### Authentication
- `POST /auth/register/` — User registration
- `POST /auth/login/` — User login
- `GET /auth/logout/` — User logout

### Groups
- `GET /groups/` — List all groups
- `POST /groups/create/` — Create new group
- `GET /groups/<id>/` — Group detail
- `POST /groups/<id>/edit/` — Edit group
- `POST /groups/<id>/delete/` — Delete group

### Expenses
- `GET /groups/<id>/expenses/` — List expenses
- `POST /groups/<id>/expenses/create/` — Add expense
- `GET /groups/<id>/expenses/<id>/` — Expense detail
- `POST /groups/<id>/expenses/<id>/edit/` — Edit expense
- `POST /groups/<id>/expenses/<id>/delete/` — Delete expense

### Balances
- `GET /groups/<id>/balances/` — View all balances
- `GET /groups/<id>/balances/<user_id>/` — User balance detail

### Settlements
- `GET /groups/<id>/settlements/` — List settlements
- `POST /groups/<id>/settlements/create/` — Record settlement
- `POST /groups/<id>/settlements/<id>/delete/` — Delete settlement

### CSV Import
- `POST /groups/<id>/import/` — Upload CSV
- `GET /groups/<id>/import/<session_id>/review/` — Review import
- `POST /groups/<id>/import/<session_id>/finalize/` — Complete import
- `POST /groups/<id>/import/<session_id>/cancel/` — Cancel import

## 🤝 Contributing

This is a personal/learning project, but suggestions are welcome!

### Code Style

- Follow PEP 8 for Python code
- Use Django conventions and best practices
- Keep views focused and single-purpose
- Write descriptive commit messages
- Add docstrings to complex functions

## 📜 License

This project is for educational purposes. Feel free to use, modify, and distribute as needed.

## 🙏 Acknowledgments

- **Django** — The web framework for perfectionists with deadlines
- **Inter font** — Beautiful typography by Rasmus Andersson
- **Glassmorphism** — Modern UI design trend

## 📧 Support

For questions or issues:
1. Check this README and TECH.md
2. Review Django documentation
3. Check the admin logs
4. Review browser console for frontend errors

## 🗺️ Roadmap

Potential future enhancements:
- [ ] REST API with Django REST Framework
- [ ] Mobile app (React Native / Flutter)
- [ ] Real-time updates with WebSockets
- [ ] Email notifications
- [ ] Receipt image uploads
- [ ] Multi-language support (i18n)
- [ ] Advanced reporting & charts
- [ ] Export to PDF/Excel
- [ ] Recurring expenses
- [ ] Budget limits and alerts
- [ ] Integration with payment apps

---

**Built with ❤️ using Django 6.0**

Last Updated: June 14, 2026
