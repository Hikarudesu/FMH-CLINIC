"""Views for POS module."""

from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q, Sum
from django.core.paginator import Paginator

from accounts.decorators import module_permission_required
from accounts.models import User
from billing.models import Service
from branches.models import Branch
from inventory.models import Product
from patients.models import Pet

from .models import CashDrawer, Sale, SaleItem, Payment, Refund
from .forms import (
    CashDrawerOpenForm, CashDrawerCloseForm, RefundForm
)


# =============================================================================
# Cash Drawer Management
# =============================================================================

@login_required
@module_permission_required('pos')
def drawer_status(request):
    """Check current drawer status and show open/close form."""
    branch = request.user.branch

    # Get open drawer for this branch
    open_drawer = CashDrawer.objects.filter(
        branch=branch, status=CashDrawer.Status.OPEN
    ).first()

    if request.method == 'POST':
        if open_drawer:
            # Close drawer
            form = CashDrawerCloseForm(request.POST)
            if form.is_valid():
                open_drawer.close_drawer(
                    user=request.user,
                    actual_cash=form.cleaned_data['actual_cash'],
                    notes=form.cleaned_data.get('notes', '')
                )
                messages.success(request, 'Cash drawer closed successfully.')
                return redirect('pos:drawer_status')
        else:
            # Open drawer
            form = CashDrawerOpenForm(request.POST)
            if form.is_valid():
                drawer = form.save(commit=False)
                drawer.branch = branch
                drawer.opened_by = request.user
                drawer.expected_cash = drawer.opening_amount
                drawer.save()
                messages.success(request, 'Cash drawer opened successfully.')
                return redirect('pos:checkout')
    else:
        form = CashDrawerOpenForm() if not open_drawer else CashDrawerCloseForm()

    # Get recent drawer history
    recent_drawers = CashDrawer.objects.filter(branch=branch).order_by('-opened_at')[:10]

    context = {
        'open_drawer': open_drawer,
        'form': form,
        'recent_drawers': recent_drawers,
    }
    return render(request, 'pos/drawer_status.html', context)


@login_required
@module_permission_required('pos', 'VIEW')
def drawer_history(request):
    """View cash drawer history."""
    branch = request.user.branch
    drawers = CashDrawer.objects.filter(branch=branch).order_by('-opened_at')

    paginator = Paginator(drawers, 20)
    page = request.GET.get('page', 1)
    drawers = paginator.get_page(page)

    return render(request, 'pos/drawer_history.html', {'drawers': drawers})


# =============================================================================
# POS Checkout Interface
# =============================================================================

@login_required
@module_permission_required('pos')
def checkout(request):
    """Main POS checkout interface."""
    branch = request.user.branch

    # Create new pending sale or get existing one
    pending_sale = Sale.objects.filter(
        branch=branch,
        cashier=request.user,
        status=Sale.Status.PENDING
    ).first()

    if not pending_sale:
        pending_sale = Sale.objects.create(
            branch=branch,
            cashier=request.user
        )

    # Get available items for the branch
    services = Service.objects.filter(
        Q(branch=branch) | Q(branch__isnull=True),
        active=True
    ).order_by('category', 'name')

    # Get branches for filter dropdown
    branches = Branch.objects.filter(is_active=True).order_by('display_order')

    # Products and medications will be fetched via AJAX based on branch selection
    # Initialize as empty querysets
    products = Product.objects.none()
    medications = Product.objects.none()

    # Get customers for dropdown (pet owners = not staff or no role)
    customers = User.objects.filter(
        is_active=True
    ).filter(
        Q(assigned_role__is_staff_role=False) | Q(assigned_role__isnull=True)
    ).order_by('first_name', 'last_name')

    context = {
        'sale': pending_sale,
        'items': pending_sale.items.all(),
        'services': services,
        'products': products,
        'medications': medications,
        'customers': customers,
        'branches': branches,
        'payment_methods': Payment.Method.choices,
    }
    return render(request, 'pos/checkout.html', context)


@login_required
@module_permission_required('pos', 'CREATE')
@require_POST
def add_item(request):
    """Add an item to the current sale via AJAX."""
    sale_id = request.POST.get('sale_id')
    item_type = request.POST.get('item_type')
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        sale = Sale.objects.get(pk=sale_id, status=Sale.Status.PENDING)
    except Sale.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sale not found'}, status=404)

    # Get the item based on type
    if item_type == 'SERVICE':
        try:
            item = Service.objects.get(pk=item_id, active=True)
            # Consolidate if exists
            existing_item = sale.items.filter(item_type=SaleItem.ItemType.SERVICE, service=item).first()
            if existing_item:
                existing_item.quantity += quantity
                existing_item.save()
                sale_item = existing_item
            else:
                sale_item = SaleItem.objects.create(
                    sale=sale,
                    item_type=SaleItem.ItemType.SERVICE,
                    service=item,
                    name=item.name,
                    unit_price=item.price,
                    quantity=quantity
                )
        except Service.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Service not found'}, status=404)

    elif item_type in ['PRODUCT', 'MEDICATION']:
        try:
            item = Product.objects.get(pk=item_id, is_available=True)
            # First check if the item relies on existing quantity
            existing_item = sale.items.filter(item_type=item_type, product=item).first()
            new_quantity = (existing_item.quantity if existing_item else 0) + quantity
            
            if item.stock_quantity < new_quantity:
                return JsonResponse({
                    'success': False,
                    'error': f'Insufficient stock. Available: {item.stock_quantity}'
                }, status=400)

            if existing_item:
                existing_item.quantity = new_quantity
                existing_item.save()
                sale_item = existing_item
            else:
                sale_item = SaleItem.objects.create(
                    sale=sale,
                    item_type=item_type,
                    product=item,
                    name=item.name,
                    unit_price=item.price,
                    quantity=quantity
                )
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid item type'}, status=400)

    return JsonResponse({
        'success': True,
        'item': {
            'id': sale_item.pk,
            'name': sale_item.name,
            'quantity': sale_item.quantity,
            'unit_price': str(sale_item.unit_price),
            'line_total': str(sale_item.line_total),
        },
        'sale': {
            'subtotal': str(sale.subtotal),
            'total': str(sale.total),
        }
    })


@login_required
@module_permission_required('pos', 'CREATE')
@require_POST
def remove_item(request):
    """Remove an item from the sale via AJAX."""
    item_id = request.POST.get('item_id')

    try:
        item = SaleItem.objects.get(pk=item_id)
        sale = item.sale
        item.delete()
        sale.calculate_totals()
    except SaleItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)

    return JsonResponse({
        'success': True,
        'sale': {
            'subtotal': str(sale.subtotal),
            'total': str(sale.total),
        }
    })


@login_required
@module_permission_required('pos', 'CREATE')
@require_POST
def update_item_quantity(request):
    """Update item quantity via AJAX."""
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        item = SaleItem.objects.get(pk=item_id)

        # Check stock for products
        if item.item_type in ['PRODUCT', 'MEDICATION'] and item.product:
            if item.product.stock_quantity < quantity:
                return JsonResponse({
                    'success': False,
                    'error': f'Insufficient stock. Available: {item.product.stock_quantity}'
                }, status=400)

        item.quantity = quantity
        item.save()
        sale = item.sale

    except SaleItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)

    return JsonResponse({
        'success': True,
        'item': {
            'id': item.pk,
            'quantity': item.quantity,
            'line_total': str(item.line_total),
        },
        'sale': {
            'subtotal': str(sale.subtotal),
            'total': str(sale.total),
        }
    })


@login_required
@module_permission_required('pos', 'CREATE')
@require_POST
def update_sale_info(request):
    """Update sale customer info and discount via AJAX."""
    sale_id = request.POST.get('sale_id')

    try:
        sale = Sale.objects.get(pk=sale_id, status=Sale.Status.PENDING)
    except Sale.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sale not found'}, status=404)

    # Track which fields to save
    update_fields = ['customer_type', 'guest_name', 'guest_phone', 'guest_email', 'notes']

    # Update customer info
    customer_type = request.POST.get('customer_type', 'WALKIN')
    sale.customer_type = customer_type

    if customer_type == 'REGISTERED':
        customer_id = request.POST.get('customer_id')
        if customer_id:
            try:
                sale.customer = User.objects.get(pk=customer_id)
                # Auto-fill guest fields from customer
                sale.guest_name = sale.customer.get_full_name()
                sale.guest_phone = getattr(sale.customer, 'phone_number', '') or ''
                sale.guest_email = sale.customer.email
                update_fields.append('customer')
            except User.DoesNotExist:
                pass
        pet_id = request.POST.get('pet_id')
        if pet_id:
            try:
                sale.pet = Pet.objects.get(pk=pet_id)
                update_fields.append('pet')
            except Pet.DoesNotExist:
                pass
    else:
        sale.customer = None
        sale.guest_name = request.POST.get('guest_name', '')
        sale.guest_phone = request.POST.get('guest_phone', '')
        sale.guest_email = request.POST.get('guest_email', '')
        update_fields.append('customer')

    # ONLY update discount if discount_amount is explicitly provided in POST
    # This prevents the payment flow from accidentally wiping the discount
    if 'discount_amount' in request.POST:
        discount = request.POST.get('discount_amount', '0')
        try:
            sale.discount_amount = Decimal(str(discount)) if discount else Decimal('0.00')
        except (ValueError, InvalidOperation):
            sale.discount_amount = Decimal('0.00')
        sale.discount_reason = request.POST.get('discount_reason', '')
        update_fields.extend(['discount_amount', 'discount_reason'])

    sale.notes = request.POST.get('notes', '')

    # Save only the fields that were updated
    sale.save(update_fields=update_fields)

    # Calculate totals (will refresh discount_amount from DB before calculating)
    sale.calculate_totals()

    # Refresh to get final values
    sale.refresh_from_db()

    return JsonResponse({
        'success': True,
        'sale': {
            'subtotal': str(sale.subtotal),
            'discount': str(sale.discount_amount),
            'discount_amount': str(sale.discount_amount),
            'discount_reason': sale.discount_reason or '',
            'total': str(sale.total),
        }
    })


@login_required
@module_permission_required('pos', 'CREATE')
@require_POST
def process_payment(request):
    """Process payment for a sale."""
    sale_id = request.POST.get('sale_id')
    method = request.POST.get('method')
    amount = Decimal(request.POST.get('amount', '0'))
    reference = request.POST.get('reference_number', '')

    try:
        sale = Sale.objects.get(pk=sale_id, status=Sale.Status.PENDING)
    except Sale.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sale not found'}, status=404)

    if not sale.items.exists():
        return JsonResponse({'success': False, 'error': 'Cannot process empty sale'}, status=400)

    # Create payment
    payment = Payment.objects.create(
        sale=sale,
        method=method,
        amount=amount,
        reference_number=reference,
        received_by=request.user
    )

    # Check if fully paid
    if sale.is_fully_paid:
        sale.complete_sale()
        return JsonResponse({
            'success': True,
            'completed': True,
            'sale': {
                'transaction_id': sale.transaction_id,
                'total': str(sale.total),
                'amount_paid': str(sale.amount_paid),
                'change_due': str(sale.change_due),
            }
        })

    return JsonResponse({
        'success': True,
        'completed': False,
        'sale': {
            'total': str(sale.total),
            'amount_paid': str(sale.amount_paid),
            'balance_due': str(sale.balance_due),
        }
    })


@login_required
@module_permission_required('pos', 'DELETE')
@require_POST
def void_sale(request, sale_id):
    """Void a sale."""
    try:
        sale = Sale.objects.get(pk=sale_id)
    except Sale.DoesNotExist:
        messages.error(request, 'Sale not found.')
        return redirect('pos:sales_list')

    reason = request.POST.get('reason', '')
    try:
        sale.void_sale(request.user, reason)
        messages.success(request, f'Sale {sale.transaction_id} has been voided.')
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('pos:sales_list')


@login_required
@module_permission_required('pos', 'DELETE')
def cancel_sale(request, sale_id):
    """Cancel a pending sale (delete it)."""
    try:
        sale = Sale.objects.get(pk=sale_id, status=Sale.Status.PENDING)
        sale.delete()
        messages.info(request, 'Sale cancelled.')
    except Sale.DoesNotExist:
        messages.error(request, 'Sale not found or already completed.')

    return redirect('pos:checkout')


# =============================================================================
# Sales List and Detail
# =============================================================================

@login_required
@module_permission_required('pos', 'VIEW')
def sales_list(request):
    """View list of sales."""
    from branches.models import Branch

    branch = request.user.branch
    sales = Sale.objects.filter(branch=branch).exclude(status=Sale.Status.PENDING)

    # Filters
    status = request.GET.get('status')
    if status:
        sales = sales.filter(status=status)

    customer_type = request.GET.get('customer_type')
    if customer_type:
        sales = sales.filter(customer_type=customer_type)

    branch_filter = request.GET.get('branch')
    if branch_filter:
        sales = sales.filter(branch_id=branch_filter)

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        sales = sales.filter(created_at__date__gte=date_from)
    if date_to:
        sales = sales.filter(created_at__date__lte=date_to)

    search = request.GET.get('q')
    if search:
        sales = sales.filter(
            Q(transaction_id__icontains=search) |
            Q(guest_name__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search)
        )

    # Calculate totals
    totals = sales.filter(status=Sale.Status.COMPLETED).aggregate(
        total_sales=Sum('total'),
        total_count=Sum('pk')
    )

    paginator = Paginator(sales.order_by('-created_at'), 10)
    page = request.GET.get('page', 1)
    sales = paginator.get_page(page)

    context = {
        'sales': sales,
        'totals': totals,
        'status_choices': Sale.Status.choices,
        'customer_type_choices': Sale.CustomerType.choices,
        'branches': Branch.objects.filter(is_active=True).order_by('name'),
    }
    return render(request, 'pos/sales_list.html', context)


@login_required
@module_permission_required('pos', 'VIEW')
def sale_detail(request, sale_id):
    """View sale details."""
    sale = get_object_or_404(Sale, pk=sale_id, branch=request.user.branch)

    context = {
        'sale': sale,
        'items': sale.items.all(),
        'payments': sale.payments.all(),
        'refunds': sale.refunds.all(),
    }
    return render(request, 'pos/sale_detail.html', context)


@login_required
@module_permission_required('pos', 'VIEW')
def receipt(request, sale_id):
    """Display receipt for printing."""
    sale = get_object_or_404(Sale, pk=sale_id)

    context = {
        'sale': sale,
        'items': sale.items.all(),
        'payments': sale.payments.all(),
    }
    return render(request, 'pos/receipt.html', context)


# =============================================================================
# AJAX Search Endpoints
# =============================================================================

@login_required
@module_permission_required('pos')
@require_GET
def search_items(request):
    """Search for items (products, medications, services) via AJAX."""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', 'all')
    branch = request.user.branch

    results = []

    if not query or len(query) < 2:
        return JsonResponse({'results': []})

    # Search services
    if category in ['all', 'service']:
        services = Service.objects.filter(
            Q(branch=branch) | Q(branch__isnull=True),
            active=True,
            name__icontains=query
        )[:10]
        for s in services:
            results.append({
                'id': s.pk,
                'type': 'SERVICE',
                'name': s.name,
                'category': s.category or 'Service',
                'price': str(s.price),
                'stock': None,
            })

    # Search products from all branches
    if category in ['all', 'product']:
        products = Product.objects.filter(
            item_type='Product',
            name__icontains=query
        ).select_related('branch')[:10]
        for p in products:
            results.append({
                'id': p.pk,
                'type': 'PRODUCT',
                'name': p.name,
                'category': 'Product',
                'price': str(p.price),
                'stock': p.stock_quantity,
            })

    # Search medications from all branches
    if category in ['all', 'medication']:
        medications = Product.objects.filter(
            item_type='Medication',
            name__icontains=query
        ).select_related('branch')[:10]
        for m in medications:
            results.append({
                'id': m.pk,
                'type': 'MEDICATION',
                'name': m.name,
                'category': 'Medication',
                'price': str(m.price),
                'stock': m.stock_quantity,
            })

    return JsonResponse({'results': results})


@login_required
@module_permission_required('pos')
@require_GET
def search_customers(request):
    """Search for customers via AJAX."""
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 2:
        return JsonResponse({'results': []})

    customers = User.objects.filter(
        is_active=True
    ).filter(
        Q(assigned_role__is_staff_role=False) | Q(assigned_role__isnull=True)
    ).filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    )[:10]

    results = []
    for c in customers:
        pets = list(c.pets.filter(is_active=True).values('id', 'name', 'species'))
        results.append({
            'id': c.pk,
            'name': c.get_full_name() or c.email,
            'email': c.email,
            'phone': getattr(c, 'phone_number', ''),
            'pets': pets,
        })

    return JsonResponse({'results': results})


@login_required
@module_permission_required('pos')
@require_GET
def filter_items_by_branch(request):
    """Filter products and medications by branch via AJAX."""
    branch_id = request.GET.get('branch_id', '').strip()

    results = []

    # Get products from selected branch or all branches
    if branch_id:
        try:
            branch = Branch.objects.get(pk=branch_id)
            products = Product.objects.filter(
                item_type='Product',
                branch=branch,
                is_available=True
            ).select_related('branch')

            medications = Product.objects.filter(
                item_type='Medication',
                branch=branch,
                is_available=True
            ).select_related('branch')
        except Branch.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Branch not found'}, status=404)
    else:
        # All branches
        products = Product.objects.filter(
            item_type='Product',
            is_available=True
        ).select_related('branch')

        medications = Product.objects.filter(
            item_type='Medication',
            is_available=True
        ).select_related('branch')

    # Add products to results
    for p in products.order_by('name'):
        results.append({
            'id': p.pk,
            'type': 'PRODUCT',
            'name': p.name,
            'price': str(p.price),
            'stock': p.stock_quantity,
            'branch_name': p.branch.name if p.branch else 'Unknown',
        })

    # Add medications to results
    for m in medications.order_by('name'):
        results.append({
            'id': m.pk,
            'type': 'MEDICATION',
            'name': m.name,
            'price': str(m.price),
            'stock': m.stock_quantity,
            'branch_name': m.branch.name if m.branch else 'Unknown',
        })

    return JsonResponse({'success': True, 'results': results})


# =============================================================================
# Refunds
# =============================================================================

@login_required
@module_permission_required('pos', 'CREATE')
def refund_request(request, sale_id):
    """Request a refund for a sale - auto-completes immediately."""
    sale = get_object_or_404(Sale, pk=sale_id, branch=request.user.branch)

    if sale.status not in [Sale.Status.COMPLETED]:
        messages.error(request, 'Only completed sales can be refunded.')
        return redirect('pos:sale_detail', sale_id=sale_id)

    # Check if sale already has any refund
    existing_refund = sale.refunds.exclude(status=Refund.Status.REJECTED).first()
    if existing_refund:
        messages.error(request, f'This sale already has a refund ({existing_refund.refund_id}).')
        return redirect('pos:sale_detail', sale_id=sale_id)

    if request.method == 'POST':
        form = RefundForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.sale = sale
            refund.requested_by = request.user
            refund.status = Refund.Status.APPROVED
            refund.approved_by = request.user
            refund.save()

            # Auto-complete the refund immediately
            try:
                refund.complete_refund(request.user)
                messages.success(request, f'Refund {refund.refund_id} has been completed.')
            except ValueError as e:
                messages.error(request, str(e))

            return redirect('pos:sale_detail', sale_id=sale_id)
    else:
        form = RefundForm(initial={'amount': sale.total})

    context = {
        'sale': sale,
        'form': form,
    }
    return render(request, 'pos/refund_request.html', context)


@login_required
@module_permission_required('pos', 'VIEW')
def refund_list(request):
    """View and manage refund requests."""
    from branches.models import Branch

    branch = request.user.branch
    refunds = Refund.objects.filter(sale__branch=branch).order_by('-created_at')

    # Filters
    status = request.GET.get('status')
    if status:
        refunds = refunds.filter(status=status)

    refund_type = request.GET.get('refund_type')
    if refund_type:
        refunds = refunds.filter(refund_type=refund_type)

    branch_filter = request.GET.get('branch')
    if branch_filter:
        refunds = refunds.filter(sale__branch_id=branch_filter)

    search = request.GET.get('q')
    if search:
        refunds = refunds.filter(
            Q(refund_id__icontains=search) |
            Q(sale__transaction_id__icontains=search) |
            Q(sale__customer__first_name__icontains=search) |
            Q(sale__customer__last_name__icontains=search) |
            Q(sale__guest_name__icontains=search)
        )

    paginator = Paginator(refunds, 10)
    page = request.GET.get('page', 1)
    refunds = paginator.get_page(page)

    context = {
        'refunds': refunds,
        'status_choices': Refund.Status.choices,
        'refund_type_choices': Refund.RefundType.choices,
        'branches': Branch.objects.filter(is_active=True).order_by('name'),
    }
    return render(request, 'pos/refund_list.html', context)


@login_required
@module_permission_required('pos', 'CREATE')
@require_POST
def refund_approve(request, refund_id):
    """Approve a refund request."""
    refund = get_object_or_404(Refund, pk=refund_id)

    if refund.status != Refund.Status.PENDING:
        messages.error(request, 'This refund is not pending.')
        return redirect('pos:refund_list')

    refund.status = Refund.Status.APPROVED
    refund.approved_by = request.user
    refund.save()
    messages.success(request, f'Refund {refund.refund_id} approved.')

    return redirect('pos:refund_list')


@login_required
@module_permission_required('pos', 'CREATE')
@require_POST
def refund_complete(request, refund_id):
    """Complete an approved refund."""
    refund = get_object_or_404(Refund, pk=refund_id)

    try:
        refund.complete_refund(request.user)
        messages.success(request, f'Refund {refund.refund_id} completed.')
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('pos:refund_list')


@login_required
@module_permission_required('pos', 'CREATE')
@require_POST
def refund_reject(request, refund_id):
    """Reject a refund request."""
    refund = get_object_or_404(Refund, pk=refund_id)

    if refund.status != Refund.Status.PENDING:
        messages.error(request, 'This refund is not pending.')
        return redirect('pos:refund_list')

    refund.status = Refund.Status.REJECTED
    refund.notes = request.POST.get('notes', '')
    refund.save()
    messages.info(request, f'Refund {refund.refund_id} rejected.')

    return redirect('pos:refund_list')
