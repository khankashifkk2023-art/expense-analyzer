"""
Custom template filters for the core app.

Usage in templates:
    {% load core_filters %}
    {{ amount|currency }}          → ₹1,200.00
    {{ amount|currency_short }}    → ₹1,200
    {{ balance|balance_color }}    → "positive" or "negative" or "zero"
"""

from decimal import Decimal
from django import template

register = template.Library()


@register.filter
def currency(value):
    """Format a number as Indian Rupee with commas and 2 decimal places."""
    try:
        value = Decimal(str(value))
        # Use Indian numbering: 1,00,000 format for lakhs
        # For simplicity, use standard comma format (acceptable for this app)
        if value < 0:
            return f"-₹{abs(value):,.2f}"
        return f"₹{value:,.2f}"
    except (ValueError, TypeError):
        return value


@register.filter
def currency_short(value):
    """Format as INR without decimal places."""
    try:
        value = Decimal(str(value))
        if value < 0:
            return f"-₹{abs(value):,.0f}"
        return f"₹{value:,.0f}"
    except (ValueError, TypeError):
        return value


@register.filter
def balance_color(value):
    """Return a CSS class name based on balance sign."""
    try:
        value = Decimal(str(value))
        if value > 0:
            return 'positive'
        elif value < 0:
            return 'negative'
        return 'zero'
    except (ValueError, TypeError):
        return 'zero'


@register.filter
def abs_value(value):
    """Return the absolute value — useful for displaying 'X owes Y ₹Z'."""
    try:
        return abs(Decimal(str(value)))
    except (ValueError, TypeError):
        return value
