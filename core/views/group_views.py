"""
Group and membership management views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from ..models import ExpenseGroup, GroupMembership
from ..forms import GroupForm, MembershipForm


@login_required
def group_list(request):
    """List all groups the user is a member of or created."""
    # Groups where user is currently a member (date_left is NULL)
    member_groups = ExpenseGroup.objects.filter(
        memberships__user=request.user,
        memberships__date_left__isnull=True
    ).distinct().order_by('-created_at')
    
    # Also include groups created by user (even if they left)
    created_groups = ExpenseGroup.objects.filter(
        created_by=request.user
    ).exclude(
        id__in=member_groups.values_list('id', flat=True)
    ).order_by('-created_at')
    
    context = {
        'member_groups': member_groups,
        'created_groups': created_groups,
    }
    return render(request, 'core/groups/group_list.html', context)


@login_required
def group_create(request):
    """Create a new expense group."""
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            
            # Automatically add creator as a member
            GroupMembership.objects.create(
                group=group,
                user=request.user,
                date_joined=group.created_at.date()
            )
            
            messages.success(request, f'Group "{group.name}" created successfully!')
            return redirect('core:group_detail', group_id=group.id)
    else:
        form = GroupForm()
    
    return render(request, 'core/groups/group_form.html', {'form': form, 'action': 'Create'})


@login_required
def group_detail(request, group_id):
    """View group details and members."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    
    # Check if user has access to this group
    is_member = group.memberships.filter(
        user=request.user,
        date_left__isnull=True
    ).exists()
    is_creator = group.created_by == request.user
    
    if not (is_member or is_creator):
        messages.error(request, 'You do not have access to this group.')
        return redirect('core:group_list')
    
    # Get active and past members
    active_members = group.memberships.filter(date_left__isnull=True).select_related('user')
    past_members = group.memberships.filter(date_left__isnull=False).select_related('user')
    
    # Get recent expenses
    recent_expenses = group.expenses.all()[:10]
    
    context = {
        'group': group,
        'active_members': active_members,
        'past_members': past_members,
        'recent_expenses': recent_expenses,
        'is_creator': is_creator,
        'is_member': is_member,
    }
    return render(request, 'core/groups/group_detail.html', context)


@login_required
def group_edit(request, group_id):
    """Edit group details."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    
    # Only creator can edit group
    if group.created_by != request.user:
        messages.error(request, 'Only the group creator can edit this group.')
        return redirect('core:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group updated successfully!')
            return redirect('core:group_detail', group_id=group.id)
    else:
        form = GroupForm(instance=group)
    
    return render(request, 'core/groups/group_form.html', {
        'form': form,
        'group': group,
        'action': 'Edit'
    })


@login_required
def group_delete(request, group_id):
    """Delete a group."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    
    # Only creator can delete group
    if group.created_by != request.user:
        messages.error(request, 'Only the group creator can delete this group.')
        return redirect('core:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f'Group "{group_name}" deleted successfully.')
        return redirect('core:group_list')
    
    return render(request, 'core/groups/group_confirm_delete.html', {'group': group})


@login_required
def member_add(request, group_id):
    """Add a member to a group."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    
    # Only creator or existing members can add new members
    if not (group.created_by == request.user or 
            group.memberships.filter(user=request.user, date_left__isnull=True).exists()):
        messages.error(request, 'You do not have permission to add members.')
        return redirect('core:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        form = MembershipForm(request.POST, group=group)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.group = group
            membership.save()
            messages.success(request, f'{membership.user.username} added to the group!')
            return redirect('core:group_detail', group_id=group.id)
    else:
        form = MembershipForm(group=group)
    
    return render(request, 'core/groups/member_form.html', {
        'form': form,
        'group': group,
        'action': 'Add'
    })


@login_required
def member_remove(request, group_id, membership_id):
    """Mark a member as having left the group."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    membership = get_object_or_404(GroupMembership, id=membership_id, group=group)
    
    # Only creator or the member themselves can remove
    if not (group.created_by == request.user or membership.user == request.user):
        messages.error(request, 'You do not have permission to remove this member.')
        return redirect('core:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        from django.utils import timezone
        membership.date_left = timezone.now().date()
        membership.save()
        messages.success(request, f'{membership.user.username} has been marked as left.')
        return redirect('core:group_detail', group_id=group.id)
    
    return render(request, 'core/groups/member_confirm_remove.html', {
        'group': group,
        'membership': membership
    })
