"""
Views for handling inventory catalog display.
"""
from datetime import date, timedelta
from collections import defaultdict

from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse

from accounts.models import User, ActivityLog
from accounts.decorators import module_permission_required
from branches.models import Branch
from notifications.models import Notification
from notifications.email_utils import send_reservation_notification
from .models import Product, StockAdjustment, Reservation, StockTransfer
from .forms import StockAdjustmentForm, ProductForm, StockTransferRequestForm


def auto_cancel_expired_reservations():
    """Finds pending reservations older than 24 hours and cancels them."""
    expiration_threshold = timezone.now() - timedelta(hours=24)
    # pylint: disable=no-member
    expired_reservations = Reservation.objects.filter(
        status=Reservation.Status.PENDING,
        created_at__lte=expiration_threshold
    ).select_related('product', 'product__branch', 'user')

    for res in expired_reservations:
        res.status = Reservation.Status.CANCELLED
        res.save()

        # Restore stock
        StockAdjustment.objects.create(
            branch=res.product.branch,
            product=res.product,
            adjustment_type='Return',
            reference=f"RSV-{res.pk}-AUTO-EXP",
            date=timezone.now().date(),
            quantity=res.quantity,
            cost_per_unit=res.product.unit_cost,
            reason="Automatically cancelled due to 24-hour expiration.",
        )

        # Notify admins (hierarchy level >= 8: Branch Admin or higher)
        admin_users = User.objects.filter(
            assigned_role__hierarchy_level__gte=8
        )
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                title="Reservation Auto-Cancelled",
                message=(
                    f"Reservation #{res.pk} for {res.quantity}x {res.product.name} "
                    f"reserved by {res.user.get_full_name() or res.user.username} "
                    f"was automatically cancelled (24h expired)."
                ),
                notification_type=Notification.NotificationType.PRODUCT_RESERVATION,
                related_object_id=res.pk,
            )

        # Notify user
        Notification.objects.create(
            user=res.user,
            title="Reservation Expired",
            message=(
                f"Your reservation for {res.quantity}x {res.product.name} "
                f"has expired after 24 hours and was cancelled."
            ),
            notification_type=Notification.NotificationType.PRODUCT_RESERVATION,
            related_object_id=res.pk,
        )


@login_required
def catalog_view(request):
    """Digital Catalog displaying products available."""
    auto_cancel_expired_reservations()

    # pylint: disable=no-member
    branches = Branch.objects.filter(is_active=True)
    products = Product.objects.all().select_related('branch')

    selected_branch_id = request.GET.get('branch')

    if selected_branch_id:
        try:
            products = products.filter(branch_id=selected_branch_id)
            selected_branch = Branch.objects.get(  # pylint: disable=no-member
                id=selected_branch_id
            )
        except Branch.DoesNotExist:  # pylint: disable=no-member
            selected_branch = None
    else:
        selected_branch = None

    # User's own reservations
    user_reservations = Reservation.objects.filter(  # pylint: disable=no-member
        user=request.user
    ).select_related('product', 'product__branch')

    # Pagination for products
    page_number = request.GET.get('page', 1)
    paginator = Paginator(products, 24)
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventory/catalog.html', {
        'products': page_obj,
        'page_obj': page_obj,
        'branches': branches,
        'selected_branch': selected_branch,
        'user_reservations': user_reservations,
    })


@login_required
@module_permission_required('inventory', 'VIEW')
def inventory_management_view(request):
    """Admin view for managing stock adjustments."""
    auto_cancel_expired_reservations()

    # pylint: disable=no-member
    adjustments = StockAdjustment.objects.all().select_related(
        'product', 'branch')

    branches = Branch.objects.filter(is_active=True)
    selected_branch_id = request.GET.get('branch')
    products = Product.objects.all().select_related('branch')

    if selected_branch_id:
        adjustments = adjustments.filter(branch_id=selected_branch_id)
        products = products.filter(branch_id=selected_branch_id)

    # Health Metrics
    total_value = sum(p.inventory_value for p in products)
    low_stock_count = sum(1 for p in products if p.status == 'Low Stock')
    out_of_stock_count = sum(
        1 for p in products if p.status == 'Out of Stock'
    )

    # Pending reservations for admin view
    # pylint: disable=no-member
    pending_reservations = Reservation.objects.filter(
        status=Reservation.Status.PENDING
    ).select_related('product', 'user')

    if selected_branch_id:
        pending_reservations = pending_reservations.filter(
            product__branch_id=selected_branch_id
        )

    return render(request, 'inventory/management.html', {
        'adjustments': adjustments,
        'products': products,
        'branches': branches,
        'selected_branch_id': selected_branch_id,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'pending_reservations': pending_reservations,
    })


@login_required
@module_permission_required('inventory', 'CREATE')
def product_create_view(request):
    """View to create a new inventory item."""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            
            # Create initial stock adjustment if stock_quantity > 0
            if product.stock_quantity > 0:
                StockAdjustment.objects.create(
                    branch=product.branch,
                    product=product,
                    adjustment_type='Purchase',
                    reference=f"NEW-ITEM-{product.pk}",
                    date=timezone.now().date(),
                    quantity=product.stock_quantity,
                    cost_per_unit=product.unit_cost,
                    reason=f"Initial stock for new item: {product.name}",
                )
            
            messages.success(request, "Item created successfully.")
            return redirect('inventory:management')
    else:
        form = ProductForm()

    return render(request, 'inventory/product_form.html', {'form': form})


@login_required
@module_permission_required('inventory', 'EDIT')
def product_edit_view(request, pk):
    """View to edit an existing inventory item."""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated successfully.")
            return redirect('inventory:management')
    else:
        form = ProductForm(instance=product)

    return render(request, 'inventory/product_form.html', {
        'form': form, 'product': product
    })


@login_required
@module_permission_required('inventory', 'CREATE')
def stock_adjustment_create_view(request):
    """Admin view to create a new stock adjustment."""
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Stock adjustment recorded successfully.")
            return redirect('inventory:management')
        else:
            messages.error(
                request,
                "Failed to record adjustment. Please check the form errors."
            )
    else:
        form = StockAdjustmentForm()

    return render(request, 'inventory/adjustment_form.html', {
        'form': form
    })


@login_required
def reserve_product_view(request, pk):
    """Handle a product reservation from the digital catalog."""
    product = get_object_or_404(Product, pk=pk)

    if request.method != 'POST':
        return redirect('inventory:catalog')

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity.")
        return redirect('inventory:catalog')
    
    pickup_date_str = request.POST.get('pickup_date')

    # Validate stock
    if quantity < 1:
        messages.error(request, "Quantity must be at least 1.")
        return redirect('inventory:catalog')

    if quantity > product.stock_quantity:
        messages.error(
            request,
            f"Not enough stock. Only {product.stock_quantity} available."
        )
        return redirect('inventory:catalog')

    # Create reservation
    reservation = Reservation.objects.create(  # pylint: disable=no-member
        user=request.user,
        product=product,
        quantity=quantity,
        pickup_date=pickup_date_str if pickup_date_str else None,
        notes=request.POST.get('notes', ''),
    )

    # Log stock adjustment
    StockAdjustment.objects.create(  # pylint: disable=no-member
        branch=product.branch,
        product=product,
        adjustment_type='Reservation',
        reference=f"RSV-{reservation.pk}",
        date=date.today(),
        quantity=quantity,  # save() enforces negative sign
        cost_per_unit=product.unit_cost,
        reason=f"Reserved by {request.user.get_full_name() or request.user.username}",
    )

    # Notify all admin users (hierarchy level >= 8: Branch Admin or higher)
    admin_users = User.objects.filter(  # pylint: disable=no-member
        assigned_role__hierarchy_level__gte=8
    )
    for admin in admin_users:
        Notification.objects.create(  # pylint: disable=no-member
            user=admin,
            title="New Product Reservation",
            message=(
                f"{request.user.get_full_name() or request.user.username} "
                f"reserved {quantity}x {product.name}."
            ),
            notification_type=Notification.NotificationType.PRODUCT_RESERVATION,
            related_object_id=reservation.pk,
        )

    # Email notification to user
    send_reservation_notification(reservation)

    return redirect('inventory:reservation_success', pk=reservation.pk)


@login_required
def reservation_success_view(request, pk):
    """Confirmation page after a successful reservation."""
    reservation = get_object_or_404(
        Reservation, pk=pk, user=request.user
    )
    return render(request, 'inventory/reservation_success.html', {
        'reservation': reservation,
    })


@login_required
def my_reservations_view(request):
    """User view for their reservation history."""
    auto_cancel_expired_reservations()
    # pylint: disable=no-member
    reservations = Reservation.objects.filter(
        user=request.user
    ).select_related('product', 'product__branch')

    return render(request, 'inventory/my_reservations.html', {
        'reservations': reservations,
    })


@login_required
@module_permission_required('inventory', 'EDIT')
def confirm_reservation_view(request, pk):
    """Admin confirms a reservation when the user arrives to pick up."""
    reservation = get_object_or_404(Reservation, pk=pk)

    if reservation.status != Reservation.Status.PENDING:
        messages.warning(request, "This reservation is no longer pending.")
        return redirect('inventory:management')

    reservation.status = Reservation.Status.RELEASED
    reservation.save()

    # Notify the user
    Notification.objects.create(  # pylint: disable=no-member
        user=reservation.user,
        title="Reservation Released",
        message=(
            f"Your reservation for {reservation.quantity}x "
            f"{reservation.product.name} has been released. "
            f"Thank you for your purchase!"
        ),
        notification_type=Notification.NotificationType.PRODUCT_RESERVATION,
        related_object_id=reservation.pk,
    )

    # Email notification
    send_reservation_notification(reservation)

    messages.success(
        request,
        f"Reservation RSV-{reservation.pk} released."
    )
    return redirect('inventory:management')


@login_required
@module_permission_required('inventory', 'DELETE')
def cancel_reservation_view(request, pk):
    """Admin cancels a reservation. Stock is restored."""
    reservation = get_object_or_404(
        Reservation, pk=pk
    )

    if reservation.status != Reservation.Status.PENDING:
        messages.warning(request, "This reservation cannot be cancelled.")
        return redirect('inventory:management')

    reservation.status = Reservation.Status.CANCELLED
    reservation.save()

    # Restore stock via a Return adjustment
    StockAdjustment.objects.create(  # pylint: disable=no-member
        branch=reservation.product.branch,
        product=reservation.product,
        adjustment_type='Return',
        reference=f"RSV-{reservation.pk}-CANCEL",
        date=date.today(),
        quantity=reservation.quantity,  # positive = stock added back
        cost_per_unit=reservation.product.unit_cost,
        reason=f"Reservation cancelled by {request.user.get_full_name() or request.user.username}",
    )

    # Notify admins (hierarchy level >= 8: Branch Admin or higher)
    admin_users = User.objects.filter(  # pylint: disable=no-member
        assigned_role__hierarchy_level__gte=8
    )
    for admin in admin_users:
        Notification.objects.create(  # pylint: disable=no-member
            user=admin,
            title="Reservation Cancelled",
            message=(
                f"Reservation for {reservation.quantity}x "
                f"{reservation.product.name} by "
                f"{reservation.user.get_full_name() or reservation.user.username} "
                f"was cancelled. Stock has been restored."
            ),
            notification_type=Notification.NotificationType.PRODUCT_RESERVATION,
            related_object_id=reservation.pk,
        )

    # Notify user it was cancelled by the clinic
    Notification.objects.create(  # pylint: disable=no-member
        user=reservation.user,
        title="Reservation Cancelled",
        message=(
            f"Your reservation for {reservation.quantity}x {reservation.product.name} "
            f"was cancelled by the clinic."
        ),
        notification_type=Notification.NotificationType.PRODUCT_RESERVATION,
        related_object_id=reservation.pk,
    )

    # Email notification
    send_reservation_notification(reservation)

    messages.success(
        request, "Reservation cancelled. Stock has been restored.")
    return redirect('inventory:management')


@login_required
@module_permission_required('stock_transfers', 'VIEW')
def stock_transfer_list_view(request):
    """List all stock transfers for the user's branch."""
    if hasattr(request.user, 'staff_profile') and request.user.staff_profile.branch:
        branch = request.user.staff_profile.branch
        transfers = StockTransfer.objects.filter(  # pylint: disable=no-member
            Q(source_product__branch=branch) | Q(destination_branch=branch)
        ).select_related(
            'source_product', 'source_product__branch',
            'destination_branch', 'requested_by', 'processed_by'
        )
    else:
        # Admin or HQ staff sees all
        transfers = StockTransfer.objects.all().select_related(  # pylint: disable=no-member
            'source_product', 'source_product__branch',
            'destination_branch', 'requested_by', 'processed_by'
        )

    context = {
        'transfers': transfers,
        'page_title': 'Stock Transfers'
    }
    return render(request, 'inventory/stock_transfer_list.html', context)


@login_required
@module_permission_required('stock_transfers', 'CREATE')
def stock_transfer_request_view(request):
    """View to request stock from another branch."""
    if not hasattr(request.user, 'staff_profile') or not request.user.staff_profile.branch:
        messages.error(
            request, "You must be assigned to a branch to request transfers.")
        return redirect('inventory:management')

    branch = request.user.staff_profile.branch

    if request.method == 'POST':
        form = StockTransferRequestForm(request.POST, user_branch=branch)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.requested_by = request.user
            transfer.save()
            messages.success(
                request,
                f"Requested {transfer.quantity}x {transfer.source_product.name} "
                f"from {transfer.source_product.branch.name}."
            )
            return redirect('inventory:transfer_list')
    else:
        form = StockTransferRequestForm(user_branch=branch)

    context = {
        'form': form,
        'page_title': 'Request Stock Transfer',
        'branch': branch
    }
    return render(request, 'inventory/stock_transfer_form.html', context)


@login_required
@module_permission_required('stock_transfers', 'MANAGE')
def stock_transfer_update_status_view(request, pk):
    """Update status of a stock transfer (Approve, Reject, Complete)."""
    transfer = get_object_or_404(StockTransfer, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        try:
            if action == 'approve':
                # Backend validation: Only allow approval of Pending transfers
                if transfer.status != StockTransfer.Status.PENDING:
                    messages.error(
                        request,
                        f"Transfer #{transfer.pk} cannot be approved - "
                        f"current status is '{transfer.status}'."
                    )
                    return redirect('inventory:transfer_list')

                transfer.status = StockTransfer.Status.APPROVED
                transfer.processed_by = request.user
                transfer.save()
                messages.success(request, f"Transfer #{transfer.pk} approved.")

            elif action == 'reject':
                # Backend validation: Only allow rejection of Pending transfers
                if transfer.status != StockTransfer.Status.PENDING:
                    messages.error(
                        request,
                        f"Transfer #{transfer.pk} cannot be rejected - "
                        f"current status is '{transfer.status}'."
                    )
                    return redirect('inventory:transfer_list')

                transfer.status = StockTransfer.Status.REJECTED
                transfer.processed_by = request.user
                transfer.save()
                messages.success(request, f"Transfer #{transfer.pk} rejected.")

            elif action == 'complete':
                # Backend validation: Only allow completion of Approved transfers
                if transfer.status != StockTransfer.Status.APPROVED:
                    messages.error(
                        request,
                        f"Transfer #{transfer.pk} cannot be completed - "
                        f"current status is '{transfer.status}'."
                    )
                    return redirect('inventory:transfer_list')

                transfer.complete_transfer(request.user)
                messages.success(
                    request, f"Transfer #{transfer.pk} completed successfully.")
        except ValueError as e:
            messages.error(request, str(e))

    return redirect('inventory:transfer_list')


@login_required
@module_permission_required('stock_monitor', 'VIEW')
def super_admin_stock_view(request):
    """
    Stock Level Monitor for Super Admin.
    Displays Low Stock alerts per branch using min_stock_level threshold.
    Allows filtering by Branch.
    """
    branch_id = request.GET.get('branch_id')
    branches = Branch.objects.filter(is_active=True)

    products = Product.objects.filter(is_deleted=False).select_related('branch')

    if branch_id:
        products = products.filter(branch_id=branch_id)
        selected_branch = get_object_or_404(Branch, pk=branch_id)
    else:
        selected_branch = None

    # Low Stock: current quantity <= min_stock_level
    low_stock = products.filter(
        stock_quantity__lte=F('min_stock_level')
    ).exclude(
        stock_quantity=0  # Exclude out of stock to show separately
    ).order_by('stock_quantity')

    # Out of Stock: quantity = 0
    out_of_stock = products.filter(stock_quantity=0).order_by('name')

    # Calculate stats
    low_stock_count = low_stock.count()
    out_of_stock_count = out_of_stock.count()
    total_critical = low_stock_count + out_of_stock_count
    
    # Total products and inventory value (across filtered products)
    total_products = products.count()
    total_inventory_value = sum(p.inventory_value for p in products)

    # Branch-wise breakdown - show ALL branches if no filter, or selected branch only
    branch_breakdown = {}
    branches_to_display = [selected_branch] if selected_branch else branches
    
    for branch in branches_to_display:
        branch_products = Product.objects.filter(
            branch=branch,
            is_deleted=False
        )
        branch_low = branch_products.filter(
            stock_quantity__lte=F('min_stock_level')
        ).exclude(stock_quantity=0).count()
        branch_out = branch_products.filter(stock_quantity=0).count()
        branch_value = sum(p.inventory_value for p in branch_products)
        branch_breakdown[branch.id] = {
            'name': branch.name,
            'low': branch_low,
            'out': branch_out,
            'total': branch_low + branch_out,
            'product_count': branch_products.count(),
            'inventory_value': branch_value
        }

    return render(request, 'inventory/stock_level_monitor.html', {
        'branches': branches,
        'selected_branch': selected_branch,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_critical': total_critical,
        'total_products': total_products,
        'total_inventory_value': total_inventory_value,
        'branch_breakdown': branch_breakdown,
        'page_title': 'Stock Level Monitor',
    })


def group_logs_by_date(logs):
    """
    Groups logs into date categories: Today, Yesterday, This Week, This Month, Older.
    Excludes overlapping entries - each log appears in only its most specific category.
    """
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Use ordered dict-like structure for clean grouping
    groups = {
        'Today': [],
        'Yesterday': [],
        'This Week': [],
        'This Month': [],
        'Older': []
    }

    for log in logs:
        log_date = log.timestamp.date() if log.timestamp else None
        if not log_date:
            continue

        # Mutually exclusive categorization (most specific first)
        if log_date == today:
            groups['Today'].append(log)
        elif log_date == yesterday:
            groups['Yesterday'].append(log)
        elif log_date >= week_start and log_date > yesterday:
            # This Week excludes Today and Yesterday
            groups['This Week'].append(log)
        elif log_date >= month_start and log_date < week_start:
            # This Month excludes This Week
            groups['This Month'].append(log)
        else:
            groups['Older'].append(log)

    # Sort each group by timestamp descending
    for key in groups:
        groups[key].sort(key=lambda x: x.timestamp, reverse=True)

    # Return only non-empty groups in order
    return [(name, logs) for name, logs in groups.items() if logs]


def group_logs_by_branch(logs):
    """Groups logs by branch."""
    grouped = defaultdict(list)
    for log in logs:
        branch_name = log.branch.name if log.branch else 'System-wide'
        grouped[branch_name].append(log)

    # Sort each group by timestamp descending
    for key in grouped:
        grouped[key].sort(key=lambda x: x.timestamp, reverse=True)

    return sorted(grouped.items(), key=lambda x: x[0])


@login_required
@module_permission_required('activity_logs', 'VIEW')
def activity_logs_view(request):
    """
    Comprehensive Activity Log with filtering by Date, Branch, and Category.
    """
    # Get all logs
    logs = ActivityLog.objects.select_related('user', 'branch').all().order_by('-timestamp')

    # Filter by branch
    branch_id = request.GET.get('branch_id')
    if branch_id:
        if branch_id == 'system':
            logs = logs.filter(branch__isnull=True)
        else:
            logs = logs.filter(branch_id=branch_id)

    # Filter by category
    category = request.GET.get('category')
    if category and category != 'all':
        logs = logs.filter(category=category)

    # Filter by date range (for grouping preference)
    date_filter = request.GET.get('date_filter', 'all')
    now = timezone.now()
    today = now.date()

    if date_filter == 'today':
        logs = logs.filter(timestamp__date=today)
    elif date_filter == 'yesterday':
        yesterday = today - timedelta(days=1)
        logs = logs.filter(timestamp__date=yesterday)
    elif date_filter == 'week':
        week_start = today - timedelta(days=today.weekday())
        logs = logs.filter(timestamp__date__gte=week_start)
    elif date_filter == 'month':
        month_start = today.replace(day=1)
        logs = logs.filter(timestamp__date__gte=month_start)

    # Determine grouping preference via GET parameter
    group_by = request.GET.get('group_by', 'date')

    context = {
        'logs': logs,
        'page_title': 'System Activity Logs',
        'branches': Branch.objects.filter(is_active=True),
        'categories': ActivityLog.Category.choices,
        'group_by': group_by,
        'selected_branch_id': branch_id,
        'selected_category': category,
        'selected_date_filter': date_filter,
    }

    # Group logs based on preference
    if group_by == 'branch':
        context['grouped_logs'] = group_logs_by_branch(logs)
        context['group_key'] = 'branch'
    elif group_by == 'category':
        context['grouped_logs'] = [(cat_label, logs.filter(category=cat_value)) 
                                    for cat_value, cat_label in ActivityLog.Category.choices]
        context['grouped_logs'] = [(name, logs_qs) for name, logs_qs in context['grouped_logs'] if logs_qs.exists()]
        context['group_key'] = 'category'
    else:  # default: group by date
        context['grouped_logs'] = group_logs_by_date(logs)
        context['group_key'] = 'date'

    return render(request, 'inventory/activity_logs.html', context)


@login_required
@module_permission_required('activity_logs', 'DELETE')
def delete_activity_log(request, pk):
    """Delete a single activity log entry."""
    if request.method == 'POST':
        log = get_object_or_404(ActivityLog, pk=pk)
        log.delete()
        messages.success(request, 'Activity log entry deleted successfully.')
    return redirect('inventory:activity_logs')


@login_required
@module_permission_required('activity_logs', 'DELETE')
def clear_activity_logs(request):
    """Clear activity logs based on filters or all logs."""
    if request.method == 'POST':
        logs = ActivityLog.objects.all()

        # Apply filters from POST data
        date_filter = request.POST.get('date_filter', 'all')
        branch_id = request.POST.get('branch_id')
        category = request.POST.get('category')

        now = timezone.now()
        today = now.date()

        # Filter by date
        if date_filter == 'today':
            logs = logs.filter(timestamp__date=today)
        elif date_filter == 'yesterday':
            yesterday = today - timedelta(days=1)
            logs = logs.filter(timestamp__date=yesterday)
        elif date_filter == 'week':
            week_start = today - timedelta(days=today.weekday())
            logs = logs.filter(timestamp__date__gte=week_start)
        elif date_filter == 'month':
            month_start = today.replace(day=1)
            logs = logs.filter(timestamp__date__gte=month_start)
        elif date_filter == 'older':
            month_start = today.replace(day=1)
            logs = logs.filter(timestamp__date__lt=month_start)

        # Filter by branch
        if branch_id:
            if branch_id == 'system':
                logs = logs.filter(branch__isnull=True)
            else:
                logs = logs.filter(branch_id=branch_id)

        # Filter by category
        if category and category != 'all':
            logs = logs.filter(category=category)

        count = logs.count()
        logs.delete()

        messages.success(request, f'Successfully cleared {count} activity log(s).')

    return redirect('inventory:activity_logs')


@login_required
@module_permission_required('inventory', 'VIEW')
def get_branch_products(request, branch_id):
    """
    AJAX endpoint to get products for a specific branch.
    Returns JSON with list of products in the branch.
    """
    branch = get_object_or_404(Branch, pk=branch_id, is_active=True)
    
    products = Product.objects.filter(
        branch=branch,
        is_deleted=False
    ).order_by('name').values('id', 'name')
    
    return JsonResponse({
        'branch_id': branch_id,
        'branch_name': branch.name,
        'products': list(products)
    })
