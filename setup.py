"""
Quick setup script for SplitLedger
Run this after installing requirements and setting up .env
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'splitledger.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import ExpenseGroup, GroupMembership
from datetime import date
from decimal import Decimal


def create_sample_data():
    """Create sample users and groups for testing."""
    print("🚀 Creating sample data for SplitLedger...\n")
    
    # Create test users
    users_data = [
        ('john', 'john@example.com', 'John Doe'),
        ('jane', 'jane@example.com', 'Jane Smith'),
        ('mike', 'mike@example.com', 'Mike Johnson'),
    ]
    
    users = {}
    for username, email, full_name in users_data:
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123'
            )
            user.first_name = full_name.split()[0]
            user.last_name = full_name.split()[1]
            user.save()
            users[username] = user
            print(f"✅ Created user: {username} (password: password123)")
        else:
            users[username] = User.objects.get(username=username)
            print(f"ℹ️  User {username} already exists")
    
    print()
    
    # Create a sample group
    if not ExpenseGroup.objects.filter(name="Apartment 4B").exists():
        group = ExpenseGroup.objects.create(
            name="Apartment 4B",
            description="Shared expenses for Apartment 4B flatmates",
            created_by=users['john']
        )
        print(f"✅ Created group: {group.name}")
        
        # Add members
        for username in ['john', 'jane', 'mike']:
            GroupMembership.objects.create(
                group=group,
                user=users[username],
                date_joined=date(2026, 1, 1)
            )
            print(f"   └─ Added member: {username}")
        
        print()
        print("🎉 Sample data created successfully!")
        print()
        print("📝 You can now login with:")
        print("   Username: john, jane, or mike")
        print("   Password: password123")
        print()
        print("🌐 Start the server with: python manage.py runserver")
        print("   Then visit: http://127.0.0.1:8000/")
    else:
        print("ℹ️  Sample group already exists")
    
    print()


def check_database():
    """Check if database is properly configured."""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful\n")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please check your .env file and ensure MySQL is running.\n")
        return False


def run_migrations():
    """Run database migrations."""
    print("🔄 Running database migrations...\n")
    from django.core.management import call_command
    try:
        call_command('migrate', '--noinput')
        print("\n✅ Migrations completed successfully\n")
        return True
    except Exception as e:
        print(f"\n❌ Migration failed: {e}\n")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print(" SplitLedger Setup Script")
    print("=" * 60)
    print()
    
    # Check database connection
    if not check_database():
        return
    
    # Run migrations
    if not run_migrations():
        return
    
    # Create sample data
    create = input("Do you want to create sample test data? (y/n): ").lower()
    if create == 'y':
        create_sample_data()
    
    print("=" * 60)
    print(" Setup Complete! 🎊")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Start the server: python manage.py runserver")
    print("3. Visit: http://127.0.0.1:8000/")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)
