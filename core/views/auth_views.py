"""
Authentication views: register, login, logout.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms import UserRegistrationForm, UserLoginForm


def register_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('core:group_list')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('core:group_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/auth/register.html', {'form': form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('core:group_list')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'core:group_list')
            return redirect(next_url)
    else:
        form = UserLoginForm()
    
    return render(request, 'core/auth/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:login')
