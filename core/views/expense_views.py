"""
Expense management views.
"""

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from ..models import ExpenseGroup, Expense, ExpenseSplit
from ..forms import ExpenseForm


@login_required
def expense_list(request, group_id):
    """List all expenses for a group."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    
    # Check access
    if not (group.memberships.filter(user=request.user, date_left__isnull=True).exists() or 
            group.created_by == request.user):
        messages.error(request, 'You do not have access to this group.')
        return redirect('core:group_list')
    
    expenses = group.expenses.filter(is_settlement=False).select_related('paid_by').order_by('-date', '-created_at')
    
    context = {
        'group': group,
        'expenses': expenses,
    }
    return render(request, 'core/expenses/expense_list.html', context)


@login_required
def expense_create(request, group_id):
    """Create a new expense."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    
    # Check access
    if not group.memberships.filter(user=request.user, date_left__isnull=True).exists():
        messages.error(request, 'Only active members can add expenses.')
        return redirect('core:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, group=group)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            
            # Convert currency to INR
            if expense.currency == 'USD':
                expense.conversion_rate = Decimal(str(settings.USD_TO_INR_RATE))
                expense.amount_inr = expense.amount_original * expense.conversion_rate
            else:
                expense.conversion_rate = Decimal('1.0000')
                expense.amount_inr = expense.amount_original
            
            expense.save()
            
            # Create splits based on split_type
            _create_expense_splits(expense, request.POST)
            
            messages.success(request, f'Expense "{expense.description}" added successfully!')
            return redirect('core:expense_list', group_id=group.id)
    else:
        form = ExpenseForm(group=group, initial={'date': timezone.now().date()})
    
    # Get active members for split UI
    active_members = group.memberships.filter(
        date_left__isnull=True
    ).select_related('user')
    
    context = {
        'form': form,
        'group': group,
        'active_members': active_members,
        'action': 'Create'
    }
    return render(request, 'core/expenses/expense_form.html', context)


@login_required
def expense_detail(request, group_id, expense_id):
    """View expense details including splits."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    expense = get_object_or_404(Expense, id=expense_id, group=group)
    
    # Check access
    if not (group.memberships.filter(user=request.user, date_left__isnull=True).exists() or 
            group.created_by == request.user):
        messages.error(request, 'You do not have access to this group.')
        return redirect('core:group_list')
    
    splits = expense.splits.all().select_related('user')
    
    context = {
        'group': group,
        'expense': expense,
        'splits': splits,
    }
    return render(request, 'core/expenses/expense_detail.html', context)


@login_required
def expense_edit(request, group_id, expense_id):
    """Edit an existing expense."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    expense = get_object_or_404(Expense, id=expense_id, group=group)
    
    # Only the person who paid can edit, or group creator
    if not (expense.paid_by == request.user or group.created_by == request.user):
        messages.error(request, 'You do not have permission to edit this expense.')
        return redirect('core:expense_detail', group_id=group.id, expense_id=expense.id)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, group=group)
        if form.is_valid():
            expense = form.save(commit=False)
            
            # Recalculate INR amount
            if expense.currency == 'USD':
                expense.conversion_rate = Decimal(str(settings.USD_TO_INR_RATE))
                expense.amount_inr = expense.amount_original * expense.conversion_rate
            else:
                expense.conversion_rate = Decimal('1.0000')
                expense.amount_inr = expense.amount_original
            
            expense.save()
            
            # Delete old splits and create new ones
            expense.splits.all().delete()
            _create_expense_splits(expense, request.POST)
            
            messages.success(request, 'Expense updated successfully!')
            return redirect('core:expense_detail', group_id=group.id, expense_id=expense.id)
    else:
        form = ExpenseForm(instance=expense, group=group)
    
    # Get active members for split UI
    active_members = group.memberships.filter(
        date_left__isnull=True
    ).select_related('user')
    
    context = {
        'form': form,
        'group': group,
        'expense': expense,
        'active_members': active_members,
        'action': 'Edit'
    }
    return render(request, 'core/expenses/expense_form.html', context)


@login_required
def expense_delete(request, group_id, expense_id):
    """Delete an expense."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    expense = get_object_or_404(Expense, id=expense_id, group=group)
    
    # Only the person who paid can delete, or group creator
    if not (expense.paid_by == request.user or group.created_by == request.user):
        messages.error(request, 'You do not have permission to delete this expense.')
        return redirect('core:expense_detail', group_id=group.id, expense_id=expense.id)
    
    if request.method == 'POST':
        description = expense.description
        expense.delete()
        messages.success(request, f'Expense "{description}" deleted successfully.')
        return redirect('core:expense_list', group_id=group.id)
    
    return render(request, 'core/expenses/expense_confirm_delete.html', {
        'group': group,
        'expense': expense
    })


# ── Helper Functions ──────────────────────────────────────────────────────

def _create_expense_splits(expense, post_data):
    """
    Create ExpenseSplit records based on split_type and form data.
    
    Expected POST data structure:
    - For equal: split_users[] = list of user IDs
    - For percentage: split_percentage_<user_id> = percentage value
    - For exact: split_exact_<user_id> = exact amount
    - For shares: split_shares_<user_id> = number of shares
    """
    split_type = expense.split_type
    total_amount = expense.amount_inr
    
    if split_type == 'equal':
        # Get all users to split among
        user_ids = post_data.getlist('split_users')
        if user_ids:
            count = len(user_ids)
            per_person = total_amount / count
            
            for user_id in user_ids:
                ExpenseSplit.objects.create(
                    expense=expense,
                    user_id=user_id,
                    share_amount=per_person,
                    raw_value=None
                )
    
    elif split_type == 'percentage':
        # Get percentage for each user
        for key, value in post_data.items():
            if key.startswith('split_percentage_'):
                user_id = key.replace('split_percentage_', '')
                percentage = Decimal(value)
                share_amount = (percentage / 100) * total_amount
                
                ExpenseSplit.objects.create(
                    expense=expense,
                    user_id=user_id,
                    share_amount=share_amount,
                    raw_value=percentage
                )
    
    elif split_type == 'exact':
        # Get exact amount for each user
        for key, value in post_data.items():
            if key.startswith('split_exact_'):
                user_id = key.replace('split_exact_', '')
                exact_amount = Decimal(value)
                
                ExpenseSplit.objects.create(
                    expense=expense,
                    user_id=user_id,
                    share_amount=exact_amount,
                    raw_value=exact_amount
                )
    
    elif split_type == 'shares':
        # Get shares for each user
        shares_data = {}
        total_shares = Decimal('0')
        
        for key, value in post_data.items():
            if key.startswith('split_shares_'):
                user_id = key.replace('split_shares_', '')
                shares = Decimal(value)
                shares_data[user_id] = shares
                total_shares += shares
        
        # Calculate share amount based on ratio
        for user_id, shares in shares_data.items():
            share_amount = (shares / total_shares) * total_amount
            
            ExpenseSplit.objects.create(
                expense=expense,
                user_id=user_id,
                share_amount=share_amount,
                raw_value=shares
            )
