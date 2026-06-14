"""
CSV import service for bulk expense import.

This service handles:
- CSV parsing and validation
- Anomaly detection (duplicates, missing fields, etc.)
- Preview before import
- Batch expense creation
"""

import csv
from decimal import Decimal, InvalidOperation
from datetime import datetime
from collections import defaultdict
from django.contrib.auth.models import User
from ...models import ImportSession, ImportAnomaly, Expense, ExpenseSplit


class CSVImportService:
    """Service for importing expenses from CSV files."""
    
    def __init__(self, import_session):
        self.session = import_session
        self.group = import_session.group
        self.anomalies = []
    
    def parse_and_validate(self, file_content):
        """
        Parse CSV and detect anomalies.
        
        Expected CSV format:
        date, description, amount, currency, paid_by, split_type, split_data, notes
        
        Returns: (clean_rows, flagged_rows_count)
        """
        reader = csv.DictReader(file_content.decode('utf-8').splitlines())
        clean_rows = []
        row_number = 1  # Start from 1 (header is 0)
        
        seen_rows = set()  # For duplicate detection
        
        for row in reader:
            row_number += 1
            anomalies_for_row = []
            
            # Check for duplicate
            row_sig = f"{row.get('date')}_{row.get('description')}_{row.get('amount')}"
            if row_sig in seen_rows:
                anomalies_for_row.append({
                    'type': 'duplicate',
                    'description': 'This row appears to be a duplicate of a previous row.',
                    'suggestion': 'Skip this row or verify if it\'s a legitimate duplicate expense.'
                })
            seen_rows.add(row_sig)
            
            # Validate required fields
            if not row.get('date'):
                anomalies_for_row.append({
                    'type': 'missing_field',
                    'description': 'Date field is missing.',
                    'suggestion': 'Add a valid date in YYYY-MM-DD format.'
                })
            
            if not row.get('description'):
                anomalies_for_row.append({
                    'type': 'missing_field',
                    'description': 'Description field is missing.',
                    'suggestion': 'Add a description for this expense.'
                })
            
            if not row.get('amount'):
                anomalies_for_row.append({
                    'type': 'missing_field',
                    'description': 'Amount field is missing.',
                    'suggestion': 'Add a valid amount.'
                })
            else:
                try:
                    amount = Decimal(row['amount'])
                    if amount == 0:
                        anomalies_for_row.append({
                            'type': 'zero_amount',
                            'description': 'Amount is zero.',
                            'suggestion': 'Verify if this is correct or skip this row.'
                        })
                    elif amount < 0:
                        anomalies_for_row.append({
                            'type': 'negative_amount',
                            'description': 'Amount is negative (possible refund).',
                            'suggestion': 'Verify if this is a refund or data entry error.'
                        })
                except (InvalidOperation, ValueError):
                    anomalies_for_row.append({
                        'type': 'format_error',
                        'description': f'Invalid amount format: {row.get("amount")}',
                        'suggestion': 'Use a valid decimal number.'
                    })
            
            # Validate currency
            currency = row.get('currency', 'INR').upper()
            if currency not in ['INR', 'USD']:
                anomalies_for_row.append({
                    'type': 'currency_mismatch',
                    'description': f'Unsupported currency: {currency}',
                    'suggestion': 'Only INR and USD are supported.'
                })
            
            # Validate paid_by user exists
            paid_by_username = row.get('paid_by', '').strip()
            if paid_by_username:
                try:
                    User.objects.get(username=paid_by_username)
                except User.DoesNotExist:
                    anomalies_for_row.append({
                        'type': 'unknown_member',
                        'description': f'User "{paid_by_username}" not found.',
                        'suggestion': 'Use an existing username or create this user first.'
                    })
            else:
                anomalies_for_row.append({
                    'type': 'missing_field',
                    'description': 'paid_by field is missing.',
                    'suggestion': 'Specify who paid for this expense.'
                })
            
            # If there are anomalies, flag this row
            if anomalies_for_row:
                for anomaly in anomalies_for_row:
                    ImportAnomaly.objects.create(
                        session=self.session,
                        row_number=row_number,
                        raw_row=row,
                        anomaly_type=anomaly['type'],
                        description=anomaly['description'],
                        suggestion=anomaly['suggestion'],
                        resolution='pending'
                    )
            else:
                clean_rows.append((row_number, row))
        
        return clean_rows, ImportAnomaly.objects.filter(session=self.session).count()
    
    def import_clean_rows(self, clean_rows):
        """
        Import clean rows as expenses.
        
        Returns: number of successfully imported rows
        """
        imported_count = 0
        
        for row_number, row_data in clean_rows:
            try:
                # Parse date
                date = datetime.strptime(row_data['date'], '%Y-%m-%d').date()
                
                # Get user
                paid_by = User.objects.get(username=row_data['paid_by'].strip())
                
                # Parse amount
                amount = Decimal(row_data['amount'])
                currency = row_data.get('currency', 'INR').upper()
                
                # Calculate INR amount
                if currency == 'USD':
                    from django.conf import settings
                    conversion_rate = Decimal(str(settings.USD_TO_INR_RATE))
                    amount_inr = amount * conversion_rate
                else:
                    conversion_rate = Decimal('1.0000')
                    amount_inr = amount
                
                # Get split type
                split_type = row_data.get('split_type', 'equal').lower().strip()
                
                # Create expense
                expense = Expense.objects.create(
                    group=self.group,
                    date=date,
                    description=row_data['description'].strip(),
                    amount_original=amount,
                    currency=currency,
                    amount_inr=amount_inr,
                    conversion_rate=conversion_rate,
                    paid_by=paid_by,
                    split_type=split_type,
                    notes=row_data.get('notes', ''),
                    is_settlement=False
                )
                
                # Create splits based on split_type
                self._create_splits_from_csv(expense, row_data, amount_inr)
                
                imported_count += 1
                
            except Exception as e:
                # Log error but continue with other rows
                ImportAnomaly.objects.create(
                    session=self.session,
                    row_number=row_number,
                    raw_row=row_data,
                    anomaly_type='format_error',
                    description=f'Import failed: {str(e)}',
                    suggestion='Check data format and try again.',
                    resolution='rejected'
                )
        
        return imported_count
    
    def _create_splits_from_csv(self, expense, row_data, amount_inr):
        """
        Create expense splits based on CSV data and split type.
        
        Supports multiple CSV formats:
        1. Equal: Just split_type=equal (splits among all active members)
        2. Percentage: username_percentage columns (e.g., john_percentage=60)
        3. Exact: username_amount columns (e.g., john_amount=500)
        4. Shares: username_shares columns (e.g., john_shares=2)
        """
        split_type = expense.split_type
        
        # Get all active members
        active_members = self.group.memberships.filter(
            date_left__isnull=True
        ).select_related('user')
        
        if split_type == 'equal':
            # Equal split among all active members
            if active_members:
                per_person = amount_inr / len(active_members)
                for membership in active_members:
                    ExpenseSplit.objects.create(
                        expense=expense,
                        user=membership.user,
                        share_amount=per_person,
                        raw_value=None
                    )
        
        elif split_type == 'percentage':
            # Look for username_percentage columns
            total_percentage = Decimal('0')
            splits_data = {}
            
            for membership in active_members:
                username = membership.user.username
                percentage_key = f'{username}_percentage'
                
                if percentage_key in row_data and row_data[percentage_key]:
                    try:
                        percentage = Decimal(str(row_data[percentage_key]))
                        splits_data[membership.user] = percentage
                        total_percentage += percentage
                    except (ValueError, InvalidOperation):
                        pass
            
            # If no percentage columns found, default to equal split
            if not splits_data:
                per_person = amount_inr / len(active_members)
                for membership in active_members:
                    ExpenseSplit.objects.create(
                        expense=expense,
                        user=membership.user,
                        share_amount=per_person,
                        raw_value=None
                    )
            else:
                # Create splits based on percentages
                for user, percentage in splits_data.items():
                    share_amount = (percentage / 100) * amount_inr
                    ExpenseSplit.objects.create(
                        expense=expense,
                        user=user,
                        share_amount=share_amount,
                        raw_value=percentage
                    )
        
        elif split_type == 'exact':
            # Look for username_amount columns
            splits_data = {}
            
            for membership in active_members:
                username = membership.user.username
                amount_key = f'{username}_amount'
                
                if amount_key in row_data and row_data[amount_key]:
                    try:
                        exact_amount = Decimal(str(row_data[amount_key]))
                        splits_data[membership.user] = exact_amount
                    except (ValueError, InvalidOperation):
                        pass
            
            # If no amount columns found, default to equal split
            if not splits_data:
                per_person = amount_inr / len(active_members)
                for membership in active_members:
                    ExpenseSplit.objects.create(
                        expense=expense,
                        user=membership.user,
                        share_amount=per_person,
                        raw_value=None
                    )
            else:
                # Create splits based on exact amounts
                for user, exact_amount in splits_data.items():
                    ExpenseSplit.objects.create(
                        expense=expense,
                        user=user,
                        share_amount=exact_amount,
                        raw_value=exact_amount
                    )
        
        elif split_type == 'shares':
            # Look for username_shares columns
            total_shares = Decimal('0')
            splits_data = {}
            
            for membership in active_members:
                username = membership.user.username
                shares_key = f'{username}_shares'
                
                if shares_key in row_data and row_data[shares_key]:
                    try:
                        shares = Decimal(str(row_data[shares_key]))
                        splits_data[membership.user] = shares
                        total_shares += shares
                    except (ValueError, InvalidOperation):
                        pass
            
            # If no shares columns found, default to equal split
            if not splits_data or total_shares == 0:
                per_person = amount_inr / len(active_members)
                for membership in active_members:
                    ExpenseSplit.objects.create(
                        expense=expense,
                        user=membership.user,
                        share_amount=per_person,
                        raw_value=None
                    )
            else:
                # Create splits based on shares
                for user, shares in splits_data.items():
                    share_amount = (shares / total_shares) * amount_inr
                    ExpenseSplit.objects.create(
                        expense=expense,
                        user=user,
                        share_amount=share_amount,
                        raw_value=shares
                    )
        
        else:
            # Unknown split type, default to equal
            if active_members:
                per_person = amount_inr / len(active_members)
                for membership in active_members:
                    ExpenseSplit.objects.create(
                        expense=expense,
                        user=membership.user,
                        share_amount=per_person,
                        raw_value=None
                    )
