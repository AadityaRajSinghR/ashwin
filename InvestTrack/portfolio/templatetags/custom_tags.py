from django import template
from django.utils import timezone

register = template.Library()

@register.simple_tag
def get_current_time():
    """Return the current time."""
    return timezone.now()

@register.filter
def format_currency(value):
    """Format a number as currency."""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"
        
@register.filter
def format_percentage(value):
    """Format a number as percentage."""
    try:
        return f"{float(value):,.2f}%"
    except (ValueError, TypeError):
        return "0.00%"

@register.filter
def convert_to_inr(value):
    """Convert USD to INR using a fixed exchange rate."""
    # Using fixed exchange rate of 1 USD = 82.5 INR (as of May 2025)
    exchange_rate = 82.5
    try:
        return float(value) * exchange_rate
    except (ValueError, TypeError):
        return 0

@register.filter
def format_inr(value):
    """Format a number as INR currency."""
    try:
        return f"₹{float(value):,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"
