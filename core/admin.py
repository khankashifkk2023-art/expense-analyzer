"""
Admin registrations for all core models.

Provides a usable admin interface for inspecting and managing data
during development and debugging.
"""

from django.contrib import admin
from .models import (
    ExpenseGroup, GroupMembership, Expense, ExpenseSplit,
    Settlement, ImportSession, ImportAnomaly,
)


# ── Inlines ─────────────────────────────────────────────────────────────────

class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 1
    fields = ('user', 'date_joined', 'date_left')


class ExpenseSplitInline(admin.TabularInline):
    model = ExpenseSplit
    extra = 0
    readonly_fields = ('user', 'share_amount', 'raw_value')


class ImportAnomalyInline(admin.TabularInline):
    model = ImportAnomaly
    extra = 0
    readonly_fields = ('row_number', 'anomaly_type', 'description', 'resolution')
    fields = ('row_number', 'anomaly_type', 'description', 'resolution', 'resolution_note')


# ── Model Admins ────────────────────────────────────────────────────────────

@admin.register(ExpenseGroup)
class ExpenseGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name',)
    inlines = [GroupMembershipInline]


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'date_joined', 'date_left')
    list_filter = ('group',)
    search_fields = ('user__username', 'group__name')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'amount_original', 'currency',
                    'amount_inr', 'paid_by', 'split_type', 'is_settlement')
    list_filter = ('group', 'currency', 'split_type', 'is_settlement')
    search_fields = ('description',)
    date_hierarchy = 'date'
    inlines = [ExpenseSplitInline]


@admin.register(ExpenseSplit)
class ExpenseSplitAdmin(admin.ModelAdmin):
    list_display = ('expense', 'user', 'share_amount')
    list_filter = ('expense__group',)


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ('date', 'paid_by', 'paid_to', 'amount_inr', 'group')
    list_filter = ('group',)
    date_hierarchy = 'date'


@admin.register(ImportSession)
class ImportSessionAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'group', 'uploaded_by', 'uploaded_at',
                    'status', 'total_rows', 'imported_rows')
    list_filter = ('status', 'group')
    inlines = [ImportAnomalyInline]


@admin.register(ImportAnomaly)
class ImportAnomalyAdmin(admin.ModelAdmin):
    list_display = ('session', 'row_number', 'anomaly_type', 'resolution')
    list_filter = ('anomaly_type', 'resolution')
