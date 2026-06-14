"""
Core models for the SplitLedger shared-expenses app.

Tables:
    expense_groups      — Groups of people sharing expenses
    group_members       — Time-bounded membership (join/leave dates)
    expenses            — Individual expenses with currency + split info
    expense_splits      — Resolved per-user share for each expense (always INR)
    settlements         — Direct payments between members (NOT expenses)
    import_sessions     — CSV import tracking
    import_anomalies    — Flagged issues found during CSV import
"""

from decimal import Decimal

from django.conf import settings
from django.db import models


# ── ExpenseGroup ────────────────────────────────────────────────────────────
# Named "ExpenseGroup" to avoid collision with django.contrib.auth.models.Group

class ExpenseGroup(models.Model):
    """A group of people sharing expenses (e.g., flatmates, trip buddies)."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_groups',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'expense_groups'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# ── GroupMembership ─────────────────────────────────────────────────────────

class GroupMembership(models.Model):
    """
    Tracks when a user was part of a group.

    - date_left = NULL means the member is still active.
    - An expense only splits across members whose [date_joined, date_left]
      range includes the expense date.
    - A user can re-join a group (new row with a new date_joined).
    """

    group = models.ForeignKey(
        ExpenseGroup,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_memberships',
    )
    date_joined = models.DateField()
    date_left = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'group_members'
        # Prevent the same user from having two overlapping memberships with
        # the same join date.
        unique_together = ('group', 'user', 'date_joined')
        ordering = ['date_joined']

    def __str__(self):
        left = self.date_left or 'present'
        return f"{self.user} in {self.group} ({self.date_joined} → {left})"

    def is_active_on(self, date):
        """Check if this membership covers the given date (inclusive)."""
        if date < self.date_joined:
            return False
        if self.date_left and date > self.date_left:
            return False
        return True


# ── Expense ─────────────────────────────────────────────────────────────────

class Expense(models.Model):
    """
    A single expense in a group.

    Stores both the original currency/amount and the converted INR amount.
    The conversion_rate field records the rate used at creation time for
    auditability — recalculation won't silently change historical data.
    """

    CURRENCY_CHOICES = [
        ('INR', 'INR — Indian Rupee'),
        ('USD', 'USD — US Dollar'),
    ]
    SPLIT_CHOICES = [
        ('equal', 'Equal'),
        ('exact', 'Exact Amounts'),
        ('percentage', 'Percentage'),
        ('shares', 'Shares / Ratio'),
    ]

    group = models.ForeignKey(
        ExpenseGroup,
        on_delete=models.CASCADE,
        related_name='expenses',
    )
    date = models.DateField()
    description = models.CharField(max_length=255)
    amount_original = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text='Amount in the original currency',
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='INR',
    )
    amount_inr = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text='Amount converted to INR (used for all balance calculations)',
    )
    # The rate used when this expense was created: amount_inr = amount_original * conversion_rate
    conversion_rate = models.DecimalField(
        max_digits=10, decimal_places=4,
        default=Decimal('1.0000'),
    )
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses_paid',
    )
    split_type = models.CharField(
        max_length=10,
        choices=SPLIT_CHOICES,
        default='equal',
    )
    # True only for rows that were detected as settlements during CSV import
    # but stored alongside expenses for audit trail.
    is_settlement = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'expenses'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} — {self.description} ({self.currency} {self.amount_original})"


# ── ExpenseSplit ────────────────────────────────────────────────────────────

class ExpenseSplit(models.Model):
    """
    The resolved share each user owes for a single expense, always in INR.

    - For the payer: their split is what they owe (their fair share of the
      expense), NOT a negative credit. The balance logic handles
      credits separately by looking at who paid_by on the Expense.
    - raw_value: stores the original percentage/shares input for display
      (e.g., 30 for 30%, or 2 for "2 shares").
    """

    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name='splits',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expense_splits',
    )
    # What this user owes for this expense, in INR
    share_amount = models.DecimalField(max_digits=12, decimal_places=2)
    # The raw input value (percentage, shares count, or exact amount)
    raw_value = models.DecimalField(
        max_digits=10, decimal_places=4,
        null=True, blank=True,
        help_text='Original input: percentage (30.0), shares (2), or exact amount',
    )

    class Meta:
        db_table = 'expense_splits'
        unique_together = ('expense', 'user')

    def __str__(self):
        return f"{self.user} owes ₹{self.share_amount} for {self.expense.description}"


# ── Settlement ──────────────────────────────────────────────────────────────

class Settlement(models.Model):
    """
    A direct payment between two group members to settle a debt.

    NOT counted as an expense. Factored into balance calculations as:
    - paid_by gets +amount credit
    - paid_to gets -amount (their debt to paid_by is reduced)
    """

    group = models.ForeignKey(
        ExpenseGroup,
        on_delete=models.CASCADE,
        related_name='settlements',
    )
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='settlements_paid',
        help_text='The person who paid (settling their debt)',
    )
    paid_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='settlements_received',
        help_text='The person who received the payment',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    amount_inr = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'settlements'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.paid_by} → {self.paid_to}: ₹{self.amount_inr} on {self.date}"


# ── ImportSession ───────────────────────────────────────────────────────────

class ImportSession(models.Model):
    """
    Tracks a single CSV import operation.

    Lifecycle: pending → reviewed → completed (or cancelled)
    """

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    group = models.ForeignKey(
        ExpenseGroup,
        on_delete=models.CASCADE,
        related_name='import_sessions',
    )
    file_name = models.CharField(max_length=255)
    # Store the uploaded file for audit purposes
    file = models.FileField(upload_to='imports/', null=True, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    total_rows = models.IntegerField(default=0)
    clean_rows = models.IntegerField(default=0)
    flagged_rows = models.IntegerField(default=0)
    imported_rows = models.IntegerField(default=0)
    skipped_rows = models.IntegerField(default=0)
    # Markdown-formatted import report stored after finalization
    report_summary = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'import_sessions'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Import #{self.pk} — {self.file_name} ({self.status})"


# ── ImportAnomaly ───────────────────────────────────────────────────────────

class ImportAnomaly(models.Model):
    """
    A single flagged issue found during CSV import.

    Every anomaly is surfaced to the user — nothing is silently swallowed.
    The user must approve, modify, or reject each flagged row before
    the import can be finalized.
    """

    ANOMALY_TYPES = [
        ('duplicate', 'Duplicate Row'),
        ('settlement_as_expense', 'Settlement Recorded as Expense'),
        ('negative_amount', 'Negative Amount (Possible Refund)'),
        ('zero_amount', 'Zero Amount'),
        ('currency_mismatch', 'Currency Mismatch / Missing Currency'),
        ('post_moveout', 'Expense After Member Move-out'),
        ('missing_field', 'Missing Required Field'),
        ('name_inconsistency', 'Inconsistent Name Spelling'),
        ('percentage_sum', 'Percentage Split Does Not Sum to 100%'),
        ('exact_sum', 'Exact Split Does Not Sum to Total'),
        ('unknown_member', 'Unknown Member'),
        ('future_date', 'Future-Dated Expense'),
        ('ambiguous_date', 'Ambiguous Date Format'),
        ('format_error', 'Format Inconsistency'),
        ('split_conflict', 'Conflicting Split Type and Data'),
        ('amount_precision', 'Unusual Amount Precision'),
    ]

    RESOLUTION_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved — Import As-Is'),
        ('modified', 'Approved — Modified Before Import'),
        ('rejected', 'Rejected — Skip Row'),
        ('auto_fixed', 'Auto-Fixed'),
    ]

    session = models.ForeignKey(
        ImportSession,
        on_delete=models.CASCADE,
        related_name='anomalies',
    )
    row_number = models.IntegerField(help_text='1-indexed row number from the CSV')
    # The original CSV row stored as a JSON dict for full auditability
    raw_row = models.JSONField()
    anomaly_type = models.CharField(max_length=30, choices=ANOMALY_TYPES)
    description = models.TextField(help_text='Human-readable explanation of the issue')
    suggestion = models.TextField(
        blank=True, default='',
        help_text='What the system recommends doing with this row',
    )
    resolution = models.CharField(
        max_length=20,
        choices=RESOLUTION_CHOICES,
        default='pending',
    )
    resolution_note = models.TextField(
        blank=True, default='',
        help_text="User's reason for their decision",
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'import_anomalies'
        ordering = ['row_number']

    def __str__(self):
        return f"Row {self.row_number}: {self.get_anomaly_type_display()}"
