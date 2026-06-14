"""
Views package — each view module is imported here for clean URL wiring.
"""

from .auth_views import register_view, login_view, logout_view
from .group_views import (
    group_list, group_create, group_detail, group_edit, group_delete,
    member_add, member_remove
)
from .expense_views import (
    expense_list, expense_create, expense_detail, expense_edit, expense_delete
)
from .balance_views import balance_view, user_balance_detail
from .settlement_views import settlement_list, settlement_create, settlement_delete
from .csv_import_views import csv_upload, csv_review, csv_finalize, csv_cancel

__all__ = [
    # Auth
    'register_view', 'login_view', 'logout_view',
    # Groups
    'group_list', 'group_create', 'group_detail', 'group_edit', 'group_delete',
    'member_add', 'member_remove',
    # Expenses
    'expense_list', 'expense_create', 'expense_detail', 'expense_edit', 'expense_delete',
    # Balances
    'balance_view', 'user_balance_detail',
    # Settlements
    'settlement_list', 'settlement_create', 'settlement_delete',
    # CSV Import
    'csv_upload', 'csv_review', 'csv_finalize', 'csv_cancel',
]
