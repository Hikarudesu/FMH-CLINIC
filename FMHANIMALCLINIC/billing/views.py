"""Views for the billing app — Services management and Statement of Account."""
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import models
from django.db.models import Q
from decimal import Decimal
import json

from accounts.decorators import module_permission_required
from accounts.decorators import ModulePermissionMixin
from accounts.models import User
from .models import Service, CustomerStatement
from .forms import ServiceForm


@login_required
@module_permission_required('clinic_services', 'VIEW')
def service_list(request):
    """View for listing all clinic services with filtering and search."""
    services = Service.objects.all()

    # Filter by status (active/inactive)
    status = request.GET.get('status')
    if status == 'active':
        services = services.filter(active=True)
    elif status == 'inactive':
        services = services.filter(active=False)

    # Filter by category
    category = request.GET.get('category')
    if category:
        services = services.filter(category=category)

    # Search by name
    search = request.GET.get('q')
    if search:
        services = services.filter(
            Q(name__icontains=search) |
            Q(category__icontains=search) |
            Q(description__icontains=search)
        )

    # Get all categories for dropdown
    all_categories = Service.objects.values_list('category', flat=True).distinct().filter(category__isnull=False, category__gt='')
    categories = sorted([c for c in all_categories if c])

    services = services.order_by('-created_at')

    context = {
        'items': services,
        'categories': categories,
        'status_choices': [('active', 'Active'), ('inactive', 'Inactive')],
    }
    return render(request, 'billing/services.html', context)


class ServiceCreateView(ModulePermissionMixin, LoginRequiredMixin, CreateView):
    """View for creating a new clinic service."""
    model = Service
    form_class = ServiceForm
    template_name = 'billing/service_form.html'
    success_url = reverse_lazy('billing:billable_items')
    module_code = 'clinic_services'
    permission_type = 'CREATE'


class ServiceUpdateView(ModulePermissionMixin, LoginRequiredMixin, UpdateView):
    """View for updating an existing clinic service."""
    model = Service
    form_class = ServiceForm
    template_name = 'billing/service_form.html'
    success_url = reverse_lazy('billing:billable_items')
    module_code = 'clinic_services'
    permission_type = 'EDIT'


@login_required
@module_permission_required('clinic_services', 'DELETE')
def service_delete(request, pk):
    """View for deleting a clinic service."""
    item = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        item.delete()
    return redirect('billing:billable_items')


# =============================================================================
# Statement of Account - Admin Management
# =============================================================================

@login_required
@module_permission_required('soa', 'CREATE')
def statement_generator_form(request):
    """
    Display blank Statement of Account form.
    Staff manually enters patient name, owner name, and service amounts.
    Form can be saved and then released to customers.
    """
    # Get recent customers for quick selection
    recent_customers = User.objects.filter(
        models.Q(assigned_role__isnull=True) | models.Q(assigned_role__is_staff_role=False),
        is_active=True
    ).order_by('first_name', 'last_name')[:20]

    context = {
        'recent_customers': recent_customers,
    }
    return render(request, 'billing/statement_generator.html', context)


@login_required
@module_permission_required('soa', 'CREATE')
@require_POST
def save_statement(request):
    """Save statement from admin form."""
    try:
        data = json.loads(request.body)

        # Create statement
        statement = CustomerStatement.objects.create(
            patient_name=data.get('patient_name', ''),
            owner_name=data.get('owner_name', ''),
            date=data.get('date'),
            customer_id=data.get('customer_id') if data.get('customer_id') else None,
            consultation_fee=Decimal(data.get('consultation_fee', '0')),
            consultation_description=data.get('consultation_description', ''),
            treatment=Decimal(data.get('treatment', '0')),
            treatment_description=data.get('treatment_description', ''),
            boarding=Decimal(data.get('boarding', '0')),
            boarding_description=data.get('boarding_description', ''),
            vaccination=Decimal(data.get('vaccination', '0')),
            vaccination_description=data.get('vaccination_description', ''),
            surgery=Decimal(data.get('surgery', '0')),
            surgery_description=data.get('surgery_description', ''),
            laboratory=Decimal(data.get('laboratory', '0')),
            laboratory_description=data.get('laboratory_description', ''),
            grooming=Decimal(data.get('grooming', '0')),
            grooming_description=data.get('grooming_description', ''),
            others=Decimal(data.get('others', '0')),
            others_description=data.get('others_description', ''),
            total_amount=Decimal(data.get('total_amount', '0')),
            deposit=Decimal(data.get('deposit', '0')),
            notes=data.get('notes', ''),
            created_by=request.user,
            branch=request.user.branch
        )

        return JsonResponse({
            'success': True,
            'message': f'Statement {statement.statement_number} saved successfully',
            'statement_id': statement.id,
            'statement_number': statement.statement_number
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@module_permission_required('soa', 'VIEW')
def statement_list(request):
    """List all statements with filtering and search."""
    statements = CustomerStatement.objects.all().order_by('-created_at')

    # Filter by branch
    branch_filter = request.GET.get('branch', '')
    if branch_filter:
        statements = statements.filter(branch_id=branch_filter)

    # Search
    search_query = request.GET.get('search', '').strip()
    if search_query:
        statements = statements.filter(
            models.Q(statement_number__icontains=search_query) |
            models.Q(patient_name__icontains=search_query) |
            models.Q(owner_name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(statements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all branches for filter dropdowns
    from branches.models import Branch
    branches = Branch.objects.all().order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'branches': branches,
        'branch_filter': branch_filter,
    }

    return render(request, 'billing/statement_list.html', context)


@login_required
@module_permission_required('soa', 'VIEW')
def statement_detail(request, statement_id):
    """View statement details."""
    statement = get_object_or_404(CustomerStatement, pk=statement_id)

    context = {
        'statement': statement,
    }

    return render(request, 'billing/statement_detail_admin.html', context)


@login_required
@module_permission_required('soa', 'EDIT')
def edit_statement(request, statement_id):
    """Edit an existing statement."""
    statement = get_object_or_404(CustomerStatement, pk=statement_id)

    if request.method == 'POST':
        data = request.POST

        # Update patient info
        statement.patient_name = data.get('patient_name', statement.patient_name)
        statement.owner_name = data.get('owner_name', statement.owner_name)
        statement.date = data.get('date', statement.date)
        statement.notes = data.get('notes', '')

        # Update customer link
        customer_id = data.get('customer_id', '').strip()
        if customer_id:
            statement.customer = User.objects.filter(pk=customer_id).first()
        else:
            statement.customer = None

        # Update service amounts and descriptions
        statement.consultation_fee = Decimal(data.get('consultation_fee', '0') or '0')
        statement.consultation_description = data.get('consultation_description', '')
        statement.treatment = Decimal(data.get('treatment', '0') or '0')
        statement.treatment_description = data.get('treatment_description', '')
        statement.boarding = Decimal(data.get('boarding', '0') or '0')
        statement.boarding_description = data.get('boarding_description', '')
        statement.vaccination = Decimal(data.get('vaccination', '0') or '0')
        statement.vaccination_description = data.get('vaccination_description', '')
        statement.surgery = Decimal(data.get('surgery', '0') or '0')
        statement.surgery_description = data.get('surgery_description', '')
        statement.laboratory = Decimal(data.get('laboratory', '0') or '0')
        statement.laboratory_description = data.get('laboratory_description', '')
        statement.grooming = Decimal(data.get('grooming', '0') or '0')
        statement.grooming_description = data.get('grooming_description', '')
        statement.others = Decimal(data.get('others', '0') or '0')
        statement.others_description = data.get('others_description', '')
        statement.deposit = Decimal(data.get('deposit', '0') or '0')

        # Recalculate total
        statement.total_amount = (
            statement.consultation_fee + statement.treatment +
            statement.boarding + statement.vaccination +
            statement.surgery + statement.laboratory +
            statement.grooming + statement.others
        )

        statement.save()
        messages.success(request, f'Statement {statement.statement_number} updated successfully.')
        return redirect('billing:statement_detail', statement_id=statement.id)

    # GET — show edit form
    pet_owners = User.objects.filter(
        models.Q(assigned_role__isnull=True) | models.Q(assigned_role__is_staff_role=False)
    ).order_by('last_name', 'first_name')
    return render(request, 'billing/statement_edit.html', {
        'statement': statement,
        'pet_owners': pet_owners,
    })


@login_required
@module_permission_required('soa', 'EDIT')
@require_POST
def release_statement(request, statement_id):
    """Release statement to customer."""
    statement = get_object_or_404(CustomerStatement, pk=statement_id)

    if statement.status != 'DRAFT':
        messages.error(request, 'Only draft statements can be released.')
        return redirect('billing:statement_detail', statement_id=statement.id)

    # Check if customer account is linked
    if not statement.customer:
        messages.error(
            request,
            'Cannot release statement: No customer account linked. '
            'Please edit the statement and link it to a customer account, '
            'or use Print for walk-in customers.'
        )
        return redirect('billing:statement_detail', statement_id=statement.id)

    try:
        statement.release_to_customer(request.user)
        messages.success(
            request,
            f'Statement {statement.statement_number} has been released to {statement.customer.get_full_name()}\'s portal.'
        )
    except Exception as e:
        messages.error(request, f'Error releasing statement: {str(e)}')

    return redirect('billing:statement_detail', statement_id=statement.id)


@login_required
@module_permission_required('soa', 'DELETE')
@require_POST
def delete_statement(request, statement_id):
    """Delete a statement."""
    statement = get_object_or_404(CustomerStatement, pk=statement_id)

    statement_number = statement.statement_number
    statement.delete()
    messages.success(request, f'Statement {statement_number} has been deleted.')

    return redirect('billing:statement_list')


# =============================================================================
# Customer Portal - Statement Viewing
# =============================================================================

@login_required
def my_statements(request):
    """Customer portal - view released statements."""
    if not request.user.is_pet_owner():
        return redirect('admin_dashboard')

    # Get released statements for this customer
    statements = CustomerStatement.objects.filter(
        customer=request.user,
        status__in=['RELEASED', 'SENT']
    ).order_by('-date')

    # Pagination
    paginator = Paginator(statements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'billing/my_statements.html', context)


@login_required
def view_statement(request, statement_id):
    """Customer portal - view specific statement."""
    statement = get_object_or_404(
        CustomerStatement,
        pk=statement_id,
        customer=request.user,
        status__in=['RELEASED', 'SENT']
    )

    # Mark as viewed if not already
    if not statement.sent_at:
        statement.sent_at = timezone.now()
        statement.save()

    context = {
        'statement': statement,
    }

    return render(request, 'billing/view_statement.html', context)

