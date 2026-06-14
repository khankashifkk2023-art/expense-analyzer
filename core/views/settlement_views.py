"""
Settlement management views.
"""

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from ..models import ExpenseGroup, Settlement
from ..forms import SettlementForm


@login_required
def settlement_list(request, group_id):
    """List all settlements for a group."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    
    # Check access
    if not (group.memberships.filter(user=request.user, date_left__isnull=True).exists() or 
            group.created_by == request.user):
        messages.error(request, 'You do not have access to this group.')
        return redirect('core:group_list')
    
    settlements = group.settlements.all().select_related('paid_by', 'paid_to').order_by('-date', '-created_at')
    
    context = {
        'group': group,
        'settlements': settlements,
    }
    return render(request, 'core/settlements/settlement_list.html', context)


@login_required
def settlement_create(request, group_id):
    """Record a new settlement (payment between members)."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    
    # Check access
    if not group.memberships.filter(user=request.user, date_left__isnull=True).exists():
        messages.error(request, 'Only active members can record settlements.')
        return redirect('core:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        form = SettlementForm(request.POST, group=group)
        if form.is_valid():
            settlement = form.save(commit=False)
            settlement.group = group
            
            # Convert currency to INR
            if settlement.currency == 'USD':
                conversion_rate = Decimal(str(settings.USD_TO_INR_RATE))
                settlement.amount_inr = settlement.amount * conversion_rate
            else:
                settlement.amount_inr = settlement.amount
            
            settlement.save()
            
            messages.success(
                request,
                f'Settlement recorded: {settlement.paid_by.username} paid '
                f'{settlement.paid_to.username} ₹{settlement.amount_inr:.2f}'
            )
            return redirect('core:balance_view', group_id=group.id)
    else:
        form = SettlementForm(group=group, initial={'date': timezone.now().date()})
    
    context = {
        'form': form,
        'group': group,
        'action': 'Record'
    }
    return render(request, 'core/settlements/settlement_form.html', context)


@login_required
def settlement_delete(request, group_id, settlement_id):
    """Delete a settlement."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    settlement = get_object_or_404(Settlement, id=settlement_id, group=group)
    
    # Only the person who paid or received can delete, or group creator
    if not (settlement.paid_by == request.user or 
            settlement.paid_to == request.user or 
            group.created_by == request.user):
        messages.error(request, 'You do not have permission to delete this settlement.')
        return redirect('core:settlement_list', group_id=group.id)
    
    if request.method == 'POST':
        settlement.delete()
        messages.success(request, 'Settlement deleted successfully.')
        return redirect('core:settlement_list', group_id=group.id)
    
    return render(request, 'core/settlements/settlement_confirm_delete.html', {
        'group': group,
        'settlement': settlement
    })
