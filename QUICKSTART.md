# SplitLedger — Quick Start Guide

Get up and running in 5 minutes! ⚡

## Prerequisites Check

Before starting, make sure you have:
- ✅ Python 3.10+ installed (`python --version`)
- ✅ MySQL 8.0+ installed and running
- ✅ pip installed (`pip --version`)

## Installation Steps

### 1. Install Dependencies (2 minutes)

```bash
# Navigate to project directory
cd c:\Users\afaqu\OneDrive\Desktop\expense

# Install Python packages
pip install -r requirements.txt
```

### 2. Configure Environment (1 minute)

Create a `.env` file (copy from `.env.example`):

```env
SECRET_KEY=django-insecure-change-this-to-random-string-12345
DEBUG=True

DB_NAME=splitledger
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD_HERE
DB_HOST=127.0.0.1
DB_PORT=3306

USD_TO_INR_RATE=83.50
```

### 3. Setup Database (1 minute)

Open MySQL and create the database:

```sql
CREATE DATABASE splitledger CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Or using command line:
```bash
mysql -u root -p -e "CREATE DATABASE splitledger CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 4. Run Setup Script (1 minute)

```bash
python setup.py
```

This will:
- Check database connection
- Run migrations
- Optionally create sample test users

**Sample Test Users Created:**
- Username: `john`, Password: `password123`
- Username: `jane`, Password: `password123`
- Username: `mike`, Password: `password123`

### 5. Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 6. Start the Server!

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

## First Time Usage

### Option A: Use Sample Data
1. Login with `john` / `password123`
2. You'll see a pre-created group "Apartment 4B"
3. Click on it and start exploring!

### Option B: Start Fresh
1. Click "Register" and create your account
2. Click "Create Group" to make your first expense group
3. Add members using their usernames
4. Start adding expenses!

## Common Tasks

### Add an Expense
1. Go to your group
2. Click "Add Expense"
3. Fill in the details
4. Select who to split with
5. Save!

### View Balances
1. Click "Balances" in the group
2. See who owes whom
3. Get smart settlement suggestions

### Record a Settlement
1. Click "Record Settlement"
2. Select who paid whom
3. Enter amount and date
4. Save!

### Import CSV Expenses
1. Prepare CSV file (see `sample_import.csv` for format)
2. Click "Import CSV" in your group
3. Upload file
4. Review flagged issues
5. Import clean rows!

## Testing the Features

### Test Expense Splitting

Try creating an expense with different split types:

**Equal Split:**
- Amount: ₹1,200
- Split among all members equally

**Percentage Split:**
- Amount: ₹30,000
- Person A: 40%, Person B: 30%, Person C: 30%
- (Note: Currently requires form update after creation)

### Test CSV Import

Use the included `sample_import.csv` file:
1. Update usernames to match your users
2. Go to group → Import CSV
3. Upload the file
4. Review and import

## Troubleshooting

### "Can't connect to database"
- Check MySQL is running: `mysql -u root -p`
- Verify credentials in `.env` file
- Ensure database exists: `SHOW DATABASES;`

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt --upgrade
```

### "No such table: expense_groups"
```bash
python manage.py migrate
```

### Static files not loading
```bash
python manage.py collectstatic
```

### Forgot admin password
```bash
python manage.py changepassword yourusername
```

## Admin Panel

Access advanced features at: **http://127.0.0.1:8000/admin/**

From here you can:
- Manage all users
- View all groups and expenses
- Inspect splits and settlements
- Review import sessions
- View anomalies

## Next Steps

Once you're comfortable with the basics:

1. 📖 Read the full **README.md** for detailed documentation
2. 🔧 Check **TECH.md** for technical stack details
3. 🎨 Customize the theme in `static/css/style.css`
4. 🚀 Deploy to production (see README.md deployment section)

## Need Help?

1. Check error messages in the terminal
2. Review browser console (F12) for frontend errors
3. Check Django logs
4. Refer to README.md and TECH.md

## Quick Reference

### URLs
- Home: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Login: http://127.0.0.1:8000/auth/login/
- Register: http://127.0.0.1:8000/auth/register/

### Sample Credentials
- john / password123
- jane / password123  
- mike / password123

### Management Commands
```bash
# Run server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Open Django shell
python manage.py shell
```

---

**Ready to split some expenses! 🎉**

Having issues? Check the full README.md for detailed troubleshooting.
