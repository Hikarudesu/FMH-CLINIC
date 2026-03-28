"""
Custom template filter: peso
Usage: {{ value|peso }}
Output: formats a numeric value as Philippine currency with comma separator.
    Examples:
        50000     → 50,000.00
        1234567.5 → 1,234,567.50
        None      → 0.00
"""

from django import template

register = template.Library()


@register.filter(name='peso')
def peso(value):
    """Format a number as Philippine peso with thousands separator and 2 decimal places."""
    if value is None or value == '':
        return '0.00'
    try:
        return f'{float(value):,.2f}'
    except (ValueError, TypeError):
        return '0.00'
