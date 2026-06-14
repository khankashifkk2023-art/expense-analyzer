"""
Balance calculation and display views.
"""

from decimal import Decimal
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from ..models import ExpenseGroup, Expense, ExpenseSplit, Settlement


@login_required
def balance_view(request, group_id):
    """Display balances for all members in a group."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    
    # Check access
    if not (group.memberships.filter(user=request.user, date_left__isnull=True).exists() or 
            group.created_by == request.user):
        messages.error(request, 'You do not have access to this group.')
        return redirect('core:group_list')
    
    # Calculate balances
    balances = _calculate_balances(group)
    
    # Calculate suggested settlements
    settlements = _suggest_settlements(balances)
    
    context = {
        'group': group,
        'balances': balances,
        'settlements': settlements,
    }
    return render(request, 'core/balances/balance_view.html', context)


@login_required
def user_balance_detail(request, group_id, user_id):
    """Show detailed breakdown of a specific user's balance."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    user = get_object_or_404(User, id=user_id)
    
    # Check access
    if not (group.memberships.filter(user=request.user, date_left__isnull=True).exists() or 
            group.created_by == request.user):
        messages.error(request, 'You do not have access to this group.')
        return redirect('core:group_list')
    
    # Get all expenses paid by this user
    expenses_paid = Expense.objects.filter(
        group=group,
        paid_by=user,
        is_settlement=False
    ).order_by('-date')
    
    # Get all expense splits for this user
    expenses_owed = ExpenseSplit.objects.filter(
        expense__group=group,
        user=user
    ).select_related('expense', 'expense__paid_by').order_by('-expense__date')
    
    # Get settlements
    settlements_paid = Settlement.objects.filter(
        group=group,
        paid_by=user
    ).order_by('-date')
    
    settlements_received = Settlement.objects.filter(
        group=group,
        paid_to=user
    ).order_by('-date')
    
    # Calculate totals
    total_paid = sum(e.amount_inr for e in expenses_paid)
    total_owed = sum(s.share_amount for s in expenses_owed)
    total_settlements_paid = sum(s.amount_inr for s in settlements_paid)
    total_settlements_received = sum(s.amount_inr for s in settlements_received)
    
    net_balance = total_paid - total_owed + total_settlements_received - total_settlements_paid
    
    context = {
        'group': group,
        'balance_user': user,
        'expenses_paid': expenses_paid,
        'expenses_owed': expenses_owed,
        'settlements_paid': settlements_paid,
        'settlements_received': settlements_received,
        'total_paid': total_paid,
        'total_owed': total_owed,
        'total_settlements_paid': total_settlements_paid,
        'total_settlements_received': total_settlements_received,
        'net_balance': net_balance,
    }
    return render(request, 'core/balances/user_balance_detail.html', context)


# ── Helper Functions ──────────────────────────────────────────────────────

def _calculate_balances(group):
    """
    Calculate net balance for each member.
    
    Balance = (Amount Paid) - (Amount Owed) + (Settlements Received) - (Settlements Paid)
    
    Positive balance = member is owed money
    Negative balance = member owes money
    """
    balances = defaultdict(lambda: Decimal('0'))
    
    # Get all active and past members
    members = User.objects.filter(
        group_memberships__group=group
    ).distinct()
    
    # Initialize balances for all members
    for member in members:
        balances[member] = Decimal('0')
    
    # Add amounts paid
    for expense in Expense.objects.filter(group=group, is_settlement=False):
        balances[expense.paid_by] += expense.amount_inr
    
    # Subtract amounts owed
    for split in ExpenseSplit.objects.filter(expense__group=group):
        balances[split.user] -= split.share_amount
    
    # Add settlements received
    for settlement in Settlement.objects.filter(group=group):
        balances[settlement.paid_to] += settlement.amount_inr
        balances[settlement.paid_by] -= settlement.amount_inr
    
    # Sort by balance (highest to lowest)
    sorted_balances = sorted(
        balances.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return sorted_balances


def _suggest_settlements(balances):
    """
    Suggest optimal settlements to minimize number of transactions.
    
    Uses a greedy algorithm: match highest creditor with highest debtor.
    """
    # Separate creditors (positive balance) and debtors (negative balance)
    creditors = [(user, amount) for user, amount in balances if amount > 0]
    debtors = [(user, abs(amount)) for user, amount in balances if amount < 0]
    
    settlements = []
    
    # Make copies so we can modify them
    creditors = list(creditors)
    debtors = list(debtors)
    
    while creditors and debtors:
        creditor, credit_amount = creditors[0]
        debtor, debt_amount = debtors[0]
        
        # Settle the smaller of the two amounts
        settle_amount = min(credit_amount, debt_amount)
        
        settlements.append({
            'from': debtor,
            'to': creditor,
            'amount': settle_amount
        })
        
        # Update balances
        credit_amount -= settle_amount
        debt_amount -= settle_amount
        
        # Remove settled parties or update their amounts
        if credit_amount == 0:
            creditors.pop(0)
        else:
            creditors[0] = (creditor, credit_amount)
        
        if debt_amount == 0:
            debtors.pop(0)
        else:
            debtors[0] = (debtor, debt_amount)
    
    return settlements
