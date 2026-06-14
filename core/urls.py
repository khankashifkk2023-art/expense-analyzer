"""
URL configuration for the core app.

All routes are namespaced under 'core' and included from splitledger/urls.py.
"""

from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'core'

urlpatterns = [
    # ── Home (Redirect to Groups) ───────────────────────────────────────
    path('', RedirectView.as_view(pattern_name='core:group_list', permanent=False), name='home'),
    
    # ── Authentication ───────────────────────────────────────────────────
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # ── Groups ───────────────────────────────────────────────────────────
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    
    # ── Group Members ────────────────────────────────────────────────────
    path('groups/<int:group_id>/members/add/', views.member_add, name='member_add'),
    path('groups/<int:group_id>/members/<int:membership_id>/remove/', views.member_remove, name='member_remove'),
    
    # ── Expenses ─────────────────────────────────────────────────────────
    path('groups/<int:group_id>/expenses/', views.expense_list, name='expense_list'),
    path('groups/<int:group_id>/expenses/create/', views.expense_create, name='expense_create'),
    path('groups/<int:group_id>/expenses/<int:expense_id>/', views.expense_detail, name='expense_detail'),
    path('groups/<int:group_id>/expenses/<int:expense_id>/edit/', views.expense_edit, name='expense_edit'),
    path('groups/<int:group_id>/expenses/<int:expense_id>/delete/', views.expense_delete, name='expense_delete'),
    
    # ── Balances ─────────────────────────────────────────────────────────
    path('groups/<int:group_id>/balances/', views.balance_view, name='balance_view'),
    path('groups/<int:group_id>/balances/<int:user_id>/', views.user_balance_detail, name='user_balance_detail'),
    
    # ── Settlements ──────────────────────────────────────────────────────
    path('groups/<int:group_id>/settlements/', views.settlement_list, name='settlement_list'),
    path('groups/<int:group_id>/settlements/create/', views.settlement_create, name='settlement_create'),
    path('groups/<int:group_id>/settlements/<int:settlement_id>/delete/', views.settlement_delete, name='settlement_delete'),
    
    # ── CSV Import ───────────────────────────────────────────────────────
    path('groups/<int:group_id>/import/', views.csv_upload, name='csv_upload'),
    path('groups/<int:group_id>/import/<int:session_id>/review/', views.csv_review, name='csv_review'),
    path('groups/<int:group_id>/import/<int:session_id>/finalize/', views.csv_finalize, name='csv_finalize'),
    path('groups/<int:group_id>/import/<int:session_id>/cancel/', views.csv_cancel, name='csv_cancel'),
]
