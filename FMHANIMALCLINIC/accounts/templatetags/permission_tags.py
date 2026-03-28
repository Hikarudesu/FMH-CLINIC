"""
Template tags for RBAC permission checking.

Usage:
    {% load permission_tags %}

    {# Check if user has access to a module #}
    {% if user|has_module:'appointments' %}
        <a href="{% url 'appointments:admin_list' %}">Appointments</a>
    {% endif %}

    {# Check specific permission level #}
    {% if user|has_module_permission:'appointments:CREATE' %}
        <button>Create Appointment</button>
    {% endif %}

    {# Check special permissions #}
    {% if user|has_special_permission:'can_view_own_payslips' %}
        <a href="{% url 'payroll:my_payslips' %}">My Payslips</a>
    {% endif %}

    {# Get user's role name #}
    {{ user|role_name }}

    {# Check if user is admin #}
    {% if user|is_admin %}
        <a href="{% url 'settings:admin_settings' %}">Settings</a>
    {% endif %}
"""
from django import template

register = template.Library()


@register.filter(name='has_module')
def has_module(user, module_code):
    """
    Check if user has access to a module (any permission level).

    Usage:
        {% if user|has_module:'appointments' %}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    return user.has_module_permission(module_code)


@register.filter(name='has_module_permission')
def has_module_permission(user, module_permission):
    """
    Check if user has a specific permission for a module.

    Args:
        module_permission: String in format 'module_code:PERMISSION_TYPE'
                          e.g., 'appointments:CREATE', 'inventory:DELETE'

    Usage:
        {% if user|has_module_permission:'appointments:CREATE' %}
            <button>Create Appointment</button>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    try:
        module_code, permission_type = module_permission.split(':')
        return user.has_module_permission(module_code, permission_type)
    except ValueError:
        # If no permission type specified, check for any access
        return user.has_module_permission(module_permission)


@register.filter(name='has_special_permission')
def has_special_permission(user, permission_code):
    """
    Check if user has a special permission.

    Usage:
        {% if user|has_special_permission:'can_view_own_payslips' %}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    return user.has_special_permission(permission_code)


@register.filter(name='role_name')
def role_name(user):
    """
    Get the display name for the user's role.

    Usage:
        <span class="role-badge">{{ user|role_name }}</span>
    """
    if not user or not user.is_authenticated:
        return ''
    return user.get_display_role()


@register.filter(name='is_admin')
def is_admin(user):
    """
    Check if user is an admin (hierarchy level >= 10 or ADMIN role).

    Usage:
        {% if user|is_admin %}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.assigned_role and user.assigned_role.hierarchy_level >= 10:
        return True

    return False


@register.filter(name='is_branch_admin')
def is_branch_admin(user):
    """
    Check if user is at least a branch admin (hierarchy level >= 8).

    Usage:
        {% if user|is_branch_admin %}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.assigned_role and user.assigned_role.hierarchy_level >= 8:
        return True

    return False


@register.filter(name='is_staff_role')
def is_staff_role(user):
    """
    Check if user has a staff role (can access admin portal).

    Usage:
        {% if user|is_staff_role %}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    return user.is_clinic_staff()


@register.filter(name='is_branch_restricted')
def is_branch_restricted(user):
    """
    Check if user's data access is restricted to their branch.

    Usage:
        {% if user|is_branch_restricted %}
            <span>Showing data for {{ user.branch.name }} only</span>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return True
    return user.is_branch_restricted()


@register.simple_tag(takes_context=True)
def can_access_module(context, module_code, permission_type=None):
    """
    Check module access with optional permission type.

    Usage:
        {% can_access_module 'appointments' as can_view_appointments %}
        {% if can_view_appointments %}
            ...
        {% endif %}

        {% can_access_module 'appointments' 'CREATE' as can_create %}
        {% if can_create %}
            <button>New Appointment</button>
        {% endif %}
    """
    user = context.get('user') or context.get('request', {}).user
    if not user or not user.is_authenticated:
        return False
    return user.has_module_permission(module_code, permission_type)


@register.simple_tag(takes_context=True)
def get_accessible_modules(context):
    """
    Get all modules the current user can access.

    Usage:
        {% get_accessible_modules as modules %}
        {% for module in modules %}
            <a href="...">{{ module.name }}</a>
        {% endfor %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return []
    return request.user.get_accessible_modules()


@register.inclusion_tag('accounts/partials/_sidebar_item.html', takes_context=True)
def sidebar_item(context, module_code, url_name, icon, label, badge_count=None):
    """
    Render a sidebar item if user has permission.

    Usage:
        {% sidebar_item 'appointments' 'appointments:admin_list' 'bx-calendar-check' 'Appointments' %}
        {% sidebar_item 'patients' 'patients:admin_list' 'bxs-dog' 'Patients' total_patients_count %}
    """
    request = context.get('request')
    user = request.user if request else None

    has_access = False
    if user and user.is_authenticated:
        has_access = user.has_module_permission(module_code)

    return {
        'has_access': has_access,
        'url_name': url_name,
        'icon': icon,
        'label': label,
        'badge_count': badge_count,
        'request': request,
    }


@register.inclusion_tag('accounts/partials/_sidebar_submenu.html', takes_context=True)
def sidebar_submenu(context, menu_id, icon, label, *items):
    """
    Render a sidebar submenu with filtered items.

    Usage:
        {% sidebar_submenu 'financeSubmenu' 'bx-wallet' 'Finance' items %}
        Where items is a list of tuples: (module_code, url_name, icon, label)
    """
    request = context.get('request')
    user = request.user if request else None

    filtered_items = []
    if user and user.is_authenticated and items:
        for item in items:
            if len(item) >= 4:
                module_code, url_name, item_icon, item_label = item[:4]
                if user.has_module_permission(module_code):
                    filtered_items.append({
                        'url_name': url_name,
                        'icon': item_icon,
                        'label': item_label,
                    })

    return {
        'menu_id': menu_id,
        'icon': icon,
        'label': label,
        'items': filtered_items,
        'has_items': bool(filtered_items),
        'request': request,
    }


# ============================================================================
# Hierarchy and Role Code Checks
# ============================================================================

@register.filter(name='has_hierarchy_level')
def has_hierarchy_level(user, min_level):
    """
    Check if user has at least the specified hierarchy level.

    Usage:
        {% if user|has_hierarchy_level:8 %}  {# Branch Admin or higher #}
            ...
        {% endif %}
        {% if user|has_hierarchy_level:6 %}  {# Veterinarian or higher #}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    try:
        min_level = int(min_level)
    except (ValueError, TypeError):
        return False

    if user.assigned_role:
        return user.assigned_role.hierarchy_level >= min_level

    return False


@register.filter(name='has_role_code')
def has_role_code(user, role_code):
    """
    Check if user has a specific role code.

    Usage:
        {% if user|has_role_code:'veterinarian' %}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    if user.assigned_role:
        return user.assigned_role.code == role_code

    return False


@register.filter(name='is_veterinarian')
def is_veterinarian(user):
    """
    Check if user has veterinarian role.
    DEPRECATED: Use has_role_code:'veterinarian' or has_hierarchy_level:6 instead.
    """
    if not user or not user.is_authenticated:
        return False

    if user.assigned_role:
        return user.assigned_role.code == 'veterinarian'

    return False


@register.filter(name='is_receptionist')
def is_receptionist(user):
    """
    Check if user has receptionist role.
    DEPRECATED: Use has_role_code:'receptionist' or has_hierarchy_level:4 instead.
    """
    if not user or not user.is_authenticated:
        return False

    if user.assigned_role:
        return user.assigned_role.code == 'receptionist'

    return False


@register.filter(name='is_vet_assistant')
def is_vet_assistant(user):
    """
    Check if user has vet assistant role.
    DEPRECATED: Use has_role_code:'vet_assistant' or has_hierarchy_level:2 instead.
    """
    if not user or not user.is_authenticated:
        return False

    if user.assigned_role:
        return user.assigned_role.code == 'vet_assistant'

    return False


# ============================================================================
# Context-aware permission checks
# ============================================================================

@register.simple_tag(takes_context=True)
def can_edit_schedule(context, schedule):
    """
    Check if user can edit a specific schedule entry.
    Vets can edit their own schedules, admins can edit any.

    Usage:
        {% can_edit_schedule schedule as can_edit %}
        {% if can_edit %}
            <button>Edit</button>
        {% endif %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return False

    user = request.user

    # Admins can edit any schedule
    if user.is_superuser or user.has_module_permission('schedule', 'EDIT'):
        return True

    # Check if this is the user's own schedule
    if hasattr(schedule, 'staff') and hasattr(schedule.staff, 'user'):
        return schedule.staff.user == user

    return False


@register.simple_tag(takes_context=True)
def can_view_payslip(context, payslip):
    """
    Check if user can view a specific payslip.
    Users can view their own, admins can view all.

    Usage:
        {% can_view_payslip payslip as can_view %}
        {% if can_view %}
            <a href="...">View Payslip</a>
        {% endif %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return False

    user = request.user

    # Admins can view all payslips
    if user.is_superuser or user.has_module_permission('payroll', 'VIEW'):
        return True

    # Check if this is the user's own payslip
    if hasattr(payslip, 'staff') and hasattr(payslip.staff, 'user'):
        if payslip.staff.user == user:
            return user.has_special_permission('can_view_own_payslips')

    return False
