"""
Django forms for the core app.

Forms are added as each deliverable is built. This module provides
a central location for all form classes.
"""

from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import ExpenseGroup, GroupMembership, Expense, Settlement, ImportSession


# ── Deliverable 2: Auth Forms ────────────────────────────────────────────

class UserRegistrationForm(UserCreationForm):
    """Extended user registration with email."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'your@email.com'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Choose a username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm password'
        })


class UserLoginForm(AuthenticationForm):
    """Styled login form."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )


# ── Deliverable 3: Group & Membership Forms ──────────────────────────────

class GroupForm(forms.ModelForm):
    """Form for creating and editing expense groups."""
    class Meta:
        model = ExpenseGroup
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Apartment 4B, Goa Trip 2026'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Optional description of this group',
                'rows': 3
            }),
        }


class MembershipForm(forms.ModelForm):
    """Form for adding members to a group."""
    class Meta:
        model = GroupMembership
        fields = ('user', 'date_joined', 'date_left')
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'date_joined': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'date_left': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'placeholder': 'Leave empty if still active'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        if self.group:
            # Only show users not already in the group (for add form)
            existing_members = self.group.memberships.values_list('user', flat=True)
            self.fields['user'].queryset = User.objects.exclude(id__in=existing_members)


# ── Deliverable 4: Expense Forms ──────────────────────────────────────────

class ExpenseForm(forms.ModelForm):
    """Form for creating and editing expenses."""
    class Meta:
        model = Expense
        fields = ('date', 'description', 'amount_original', 'currency', 
                  'paid_by', 'split_type', 'notes')
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Groceries, Electricity Bill'
            }),
            'amount_original': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'placeholder': '0.00',
                'data-type': 'currency'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'paid_by': forms.Select(attrs={'class': 'form-select'}),
            'split_type': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Optional notes',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        if self.group:
            # Only show active members of this group as payer options
            active_members = User.objects.filter(
                group_memberships__group=self.group,
                group_memberships__date_left__isnull=True
            ).distinct()
            self.fields['paid_by'].queryset = active_members


class ExpenseSplitFormSet(forms.BaseInlineFormSet):
    """Formset for expense splits with validation."""
    
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        
        split_type = self.instance.split_type if self.instance else 'equal'
        total_amount = self.instance.amount_inr if self.instance else Decimal('0')
        
        if split_type == 'percentage':
            total_percentage = sum(
                form.cleaned_data.get('raw_value', 0) 
                for form in self.forms 
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
            )
            if abs(total_percentage - 100) > 0.01:
                raise ValidationError(f'Percentages must sum to 100% (got {total_percentage}%)')
        
        elif split_type == 'exact':
            total_split = sum(
                form.cleaned_data.get('share_amount', 0) 
                for form in self.forms 
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
            )
            if abs(total_split - total_amount) > 0.01:
                raise ValidationError(f'Exact amounts must sum to total expense ₹{total_amount}')


# ── Deliverable 6: Settlement Forms ───────────────────────────────────────

class SettlementForm(forms.ModelForm):
    """Form for recording settlements (payments between members)."""
    class Meta:
        model = Settlement
        fields = ('paid_by', 'paid_to', 'amount', 'currency', 'date', 'note')
        widgets = {
            'paid_by': forms.Select(attrs={'class': 'form-select'}),
            'paid_to': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'placeholder': '0.00',
                'data-type': 'currency'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Optional note about this settlement',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        if self.group:
            # Only show active members of this group
            active_members = User.objects.filter(
                group_memberships__group=self.group,
                group_memberships__date_left__isnull=True
            ).distinct()
            self.fields['paid_by'].queryset = active_members
            self.fields['paid_to'].queryset = active_members

    def clean(self):
        cleaned_data = super().clean()
        paid_by = cleaned_data.get('paid_by')
        paid_to = cleaned_data.get('paid_to')
        
        if paid_by and paid_to and paid_by == paid_to:
            raise ValidationError("A member cannot settle a payment with themselves.")
        
        return cleaned_data


# ── Deliverable 7: CSV Import Forms ───────────────────────────────────────

class CSVUploadForm(forms.ModelForm):
    """Form for uploading CSV files for expense import."""
    class Meta:
        model = ImportSession
        fields = ('file',)
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-file',
                'accept': '.csv'
            })
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith('.csv'):
                raise ValidationError('Only CSV files are supported.')
            if file.size > 5 * 1024 * 1024:  # 5 MB limit
                raise ValidationError('File size must be under 5 MB.')
        return file
