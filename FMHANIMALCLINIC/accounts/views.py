"""Views for the accounts app."""
# pylint: disable=no-member,import-outside-toplevel

import json
from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Count, Sum, Q, F
from django.db.models.functions import TruncDate
from django.core.serializers.json import DjangoJSONEncoder

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from branches.models import Branch
from .models import User
from .decorators import module_permission_required, admin_only
from .forms import PetOwnerRegistrationForm


def login_view(request):
    """Login page — redirects to correct portal after login."""
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.user.is_authenticated:
        if next_url:
            return redirect(next_url)
        if request.user.is_clinic_staff():
            # Redirect based on specific role
            if request.user.assigned_role and request.user.assigned_role.code == 'veterinarian':
                return redirect('vet_dashboard')
            elif request.user.assigned_role and request.user.assigned_role.code == 'receptionist':
                return redirect('receptionist_dashboard')
            else:
                return redirect('admin_dashboard')
        return redirect('user_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in.')

            if next_url:
                return redirect(next_url)
            if user.is_clinic_staff():
                # Redirect based on specific role
                if user.assigned_role and user.assigned_role.code == 'veterinarian':
                    return redirect('vet_dashboard')
                elif user.assigned_role and user.assigned_role.code == 'receptionist':
                    return redirect('receptionist_dashboard')
                else:
                    return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'accounts/login.html')


def register_view(request):
    """Register page view for Pet Owner registration"""
    if request.method == 'POST':
        form = PetOwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login after registration
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('select_branch')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PetOwnerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def select_branch_view(request):
    """Branch selection page — shown after pet owner registration."""
    branches = Branch.objects.filter(is_active=True)

    if request.method == 'POST':
        branch_id = request.POST.get('branch_id')
        if branch_id:
            branch = get_object_or_404(Branch, id=branch_id, is_active=True)
            request.user.branch = branch
            request.user.save(update_fields=['branch'])
            messages.success(
                request, f'Welcome! You are now registered at {branch.name}.')
        return redirect('user_dashboard')

    return render(request, 'accounts/select_branch.html', {'branches': branches})


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('landing_page')


@login_required
def user_dashboard_view(request):
    """User portal dashboard with follow-ups, appointments, and notifications."""
    from notifications.models import FollowUp, Notification
    from appointments.models import Appointment
    from patients.models import Pet

    today = date.today()

    # Pet count
    pet_count = request.user.pets.count()

    # Upcoming appointments (next 7 days) - filter out deleted pets
    upcoming_appointments = Appointment.objects.filter(
        user=request.user,
        pet__isnull=False,
        appointment_date__gte=today,
        appointment_date__lte=today + timedelta(days=7),
    ).exclude(status='CANCELLED').select_related(
        'branch', 'preferred_vet'
    ).order_by('appointment_date', 'appointment_time')
    upcoming_count = upcoming_appointments.count()

    # Follow-ups for this user's appointments
    follow_ups = FollowUp.objects.filter(
        appointment__user=request.user,
        is_completed=False,
        follow_up_date__gte=today,
    ).order_by('follow_up_date')
    follow_up_count = follow_ups.count()

    # Unread notifications
    unread_notif_count = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()

    # Recent activities (UserActivity)
    from accounts.models import UserActivity
    activities_list = UserActivity.objects.filter(user=request.user).order_by('-timestamp')
    
    paginator = Paginator(activities_list, 5)  # Show 5 activities per page
    page_number = request.GET.get('page')
    recent_activities = paginator.get_page(page_number)

    # Pet species breakdown
    pet_species_breakdown = request.user.pets.values('species').annotate(count=Count('id')).order_by('-count')

    # Vaccination appointments tracking
    vaccination_appointments = Appointment.objects.filter(
        user=request.user,
        pet__isnull=False,
        reason=Appointment.Reason.VACCINATION,
        appointment_date__gte=today - timedelta(days=30),
        appointment_date__lte=today,
    ).count()

    # Appointment cancellation stats (past 30 days)
    cancelled_appointments_count = Appointment.objects.filter(
        user=request.user,
        status='CANCELLED',
        appointment_date__gte=today - timedelta(days=30),
    ).count()

    # Appointments this month
    month_start = date(today.year, today.month, 1)
    if today.month == 12:
        month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    appointments_this_month = Appointment.objects.filter(
        user=request.user,
        pet__isnull=False,
        appointment_date__range=[month_start, month_end],
    ).exclude(status='CANCELLED').count()

    # Reservation tracking (pending/approved)
    pending_reservations = Appointment.objects.filter(
        user=request.user,
        pet__isnull=False,
        status='PENDING',
        appointment_date__gte=today,
    ).count()

    approved_reservations = Appointment.objects.filter(
        user=request.user,
        pet__isnull=False,
        status='CONFIRMED',
        appointment_date__gte=today,
    ).count()

    return render(request, 'accounts/user_dashboard.html', {
        'pet_count': pet_count,
        'upcoming_appointments': upcoming_appointments[:5],
        'upcoming_count': upcoming_count,
        'follow_ups': follow_ups,
        'follow_up_count': follow_up_count,
        'unread_notif_count': unread_notif_count,
        'recent_activities': recent_activities,
        'pet_species_breakdown': pet_species_breakdown,
        'vaccination_appointments': vaccination_appointments,
        'cancelled_appointments_count': cancelled_appointments_count,
        'appointments_this_month': appointments_this_month,
        'pending_reservations': pending_reservations,
        'approved_reservations': approved_reservations,
    })


@login_required
def profile_view(request):
    """User profile page."""
    from .forms import UserProfileUpdateForm
    if request.method == 'POST':
        form = UserProfileUpdateForm(
            request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileUpdateForm(instance=request.user)

    if request.user.is_clinic_staff():
        template_name = 'accounts/profile_admin.html'
    else:
        template_name = 'accounts/profile.html'

    return render(request, template_name, {
        'user': request.user,
        'form': form,
    })


@login_required
@module_permission_required('dashboard')
def admin_dashboard_view(request):
    """Admin portal dashboard — restricted to clinic staff roles."""
    from appointments.models import Appointment
    from patients.models import Pet
    from employees.models import StaffMember
    from notifications.models import Notification
    from pos.models import Sale, Payment
    from inventory.models import Product
    from billing.models import Service

    # Check if user is a veterinarian and redirect to vet dashboard
    if request.user.assigned_role and request.user.assigned_role.code == 'veterinarian':
        return redirect('vet_dashboard')

    # Check if user is a receptionist and redirect to receptionist dashboard
    if request.user.assigned_role and request.user.assigned_role.code == 'receptionist':
        return redirect('receptionist_dashboard')

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    # ── Today's appointments (filter out deleted pets) ──
    todays_appointments = Appointment.objects.filter(
        appointment_date=today,
        pet__isnull=False,
    ).select_related('branch', 'preferred_vet').order_by('appointment_time')

    today_count = todays_appointments.count()
    today_confirmed = todays_appointments.filter(status='CONFIRMED').count()
    today_pending = todays_appointments.filter(status='PENDING').count()

    # ── Active patients ──
    patient_count = Pet.objects.count()

    # ── Staff ──
    total_staff = StaffMember.objects.count()
    active_staff = StaffMember.objects.filter(is_active=True).count()

    # ── Branches ──
    branches = Branch.objects.filter(is_active=True)

    # ── Recent appointments (activity) ──
    # Filter out appointments where the pet has been deleted (pet=NULL)
    recent_appointments = Appointment.objects.filter(
        pet__isnull=False
    ).select_related(
        'branch', 'preferred_vet'
    ).order_by('-created_at')[:5]

    # ── Unread notifications ──
    unread_notif_count = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()

    # ─── COMPREHENSIVE ANALYTICS ───

    # Revenue chart data (last 7 days)
    revenue_by_day = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        daily_revenue = Sale.objects.filter(
            branch=request.user.branch,
            created_at__date=day,
            status='COMPLETED'
        ).aggregate(total=Sum('total'))['total'] or 0
        revenue_by_day.append({
            'date': day.strftime('%a'),
            'revenue': float(daily_revenue)
        })

    # Appointment by status breakdown
    appointment_status_breakdown = [
        {'status': 'Pending', 'count': Appointment.objects.filter(status='PENDING', pet__isnull=False).count()},
        {'status': 'Confirmed', 'count': Appointment.objects.filter(status='CONFIRMED', pet__isnull=False).count()},
        {'status': 'Completed', 'count': Appointment.objects.filter(status='COMPLETED', pet__isnull=False).count()},
        {'status': 'Cancelled', 'count': Appointment.objects.filter(status='CANCELLED', pet__isnull=False).count()},
    ]

    # Branch-wise appointment statistics
    branch_appointments = Branch.objects.filter(is_active=True).annotate(
        appointment_count=Count('appointments', filter=Q(appointments__pet__isnull=False)),
        completed_count=Count('appointments', filter=Q(
            appointments__pet__isnull=False,
            appointments__status='COMPLETED'
        ))
    ).values('name', 'appointment_count', 'completed_count')

    # Staff performance metrics
    staff_performance = StaffMember.objects.filter(is_active=True).annotate(
        total_appointments=Count('appointments', filter=Q(appointments__pet__isnull=False)),
        completed_appointments=Count('appointments', filter=Q(
            appointments__pet__isnull=False,
            appointments__status='COMPLETED'
        ))
    ).values('first_name', 'last_name', 'total_appointments', 'completed_appointments')

    # Inventory value calculation
    total_inventory_value = sum(
        product.inventory_value for product in Product.objects.all()
    ) or 0

    # Expiring products list (next 30 days)
    expiring_products = Product.objects.filter(
        expiration_date__isnull=False,
        expiration_date__gte=today,
        expiration_date__lte=today + timedelta(days=30),
        is_available=True
    ).order_by('expiration_date')[:10]

    # Pet species breakdown
    pet_species_breakdown_query = Pet.objects.values('species').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Convert to list and calculate percentages
    pet_species_breakdown = list(pet_species_breakdown_query)
    if pet_species_breakdown:
        max_count = pet_species_breakdown[0]['count'] or 1
        pet_count = sum(item['count'] for item in pet_species_breakdown)
        for species in pet_species_breakdown:
            species['percentage'] = (species['count'] / pet_count * 100) if pet_count > 0 else 0

    # Appointment sources (WALKIN vs PORTAL)
    appointment_sources = {
        'WALKIN': Appointment.objects.filter(
            source='WALKIN', pet__isnull=False
        ).count(),
        'PORTAL': Appointment.objects.filter(
            source='PORTAL', pet__isnull=False
        ).count(),
    }

    # Business metrics
    total_revenue_this_week = Sale.objects.filter(
        created_at__date__range=[week_start, week_end],
        status='COMPLETED'
    ).aggregate(total=Sum('total'))['total'] or 0

    total_revenue_last_week = Sale.objects.filter(
        created_at__date__range=[week_start - timedelta(days=7), week_start - timedelta(days=1)],
        status='COMPLETED'
    ).aggregate(total=Sum('total'))['total'] or 0

    revenue_growth = (
        ((total_revenue_this_week - total_revenue_last_week) / total_revenue_last_week * 100)
        if total_revenue_last_week > 0 else 0
    )

    total_cancelled = Appointment.objects.filter(
        status='CANCELLED', pet__isnull=False
    ).count()
    total_appointments = Appointment.objects.filter(
        pet__isnull=False
    ).count()
    cancellation_rate = (
        (total_cancelled / total_appointments * 100)
        if total_appointments > 0 else 0
    )

    # New patients this week
    new_patients_this_week = Pet.objects.filter(
        created_at__date__range=[week_start, today]
    ).count()

    # Customer analytics (new vs returning)
    new_customers_this_week = Appointment.objects.filter(
        created_at__date__range=[week_start, today],
        is_returning_customer=False,
        pet__isnull=False
    ).values('user').distinct().count()

    returning_customers_this_week = Appointment.objects.filter(
        created_at__date__range=[week_start, today],
        is_returning_customer=True,
        pet__isnull=False
    ).values('user').distinct().count()

    # Service breakdown (consultation types)
    service_breakdown_query = Service.objects.filter(
        branch=request.user.branch
    ).annotate(
        usage_count=Count('sale_items__sale', filter=Q(sale_items__sale__status='COMPLETED'))
    ).values('name', 'usage_count').order_by('-usage_count')[:10]
    
    # Convert to list and calculate percentages
    service_breakdown = list(service_breakdown_query)
    if service_breakdown:
        max_count = service_breakdown[0]['usage_count'] or 1
        for service in service_breakdown:
            service['percentage'] = (service['usage_count'] / max_count * 100) if max_count > 0 else 0

    # Payment method statistics
    payment_method_stats = Payment.objects.filter(
        sale__status='COMPLETED'
    ).values('method').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-count')

    # Pet health status distribution
    pet_health_stats = [
        {'status': 'HEALTHY', 'count': Pet.objects.filter(status='HEALTHY').count()},
        {'status': 'MONITOR', 'count': Pet.objects.filter(status='MONITOR').count()},
        {'status': 'TREATMENT', 'count': Pet.objects.filter(status='TREATMENT').count()},
        {'status': 'SURGERY', 'count': Pet.objects.filter(status='SURGERY').count()},
        {'status': 'DIAGNOSTICS', 'count': Pet.objects.filter(status='DIAGNOSTICS').count()},
        {'status': 'CRITICAL', 'count': Pet.objects.filter(status='CRITICAL').count()},
    ]

    # Low stock alerts and refunds
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=F('min_stock_level'),
        is_available=True
    ).order_by('stock_quantity')[:10]
    
    low_stock_count = low_stock_products.count()

    refunds_today = Sale.objects.filter(
        created_at__date=today,
        status='REFUNDED'
    ).aggregate(total=Sum('total'))['total'] or 0

    # Convert data to JSON for charts (use DjangoJSONEncoder for Decimal support)
    revenue_by_day_json = json.dumps(revenue_by_day, cls=DjangoJSONEncoder)
    appointment_status_breakdown_json = json.dumps(appointment_status_breakdown, cls=DjangoJSONEncoder)
    pet_species_breakdown_json = json.dumps(pet_species_breakdown, cls=DjangoJSONEncoder)
    payment_method_stats_list = list(payment_method_stats)
    payment_method_stats_json = json.dumps(payment_method_stats_list, cls=DjangoJSONEncoder)
    appointment_sources_json = json.dumps([
        {'source': 'Walk-in', 'count': appointment_sources['WALKIN']},
        {'source': 'Online Portal', 'count': appointment_sources['PORTAL']}
    ], cls=DjangoJSONEncoder)

    return render(request, 'accounts/admin_dashboard.html', {
        'today_count': today_count,
        'today_confirmed': today_confirmed,
        'today_pending': today_pending,
        'patient_count': patient_count,
        'total_staff': total_staff,
        'active_staff': active_staff,
        'branches': branches,
        'todays_appointments': todays_appointments[:10],
        'recent_appointments': recent_appointments,
        'unread_notif_count': unread_notif_count,
        'revenue_by_day': revenue_by_day_json,
        'appointment_status_breakdown': appointment_status_breakdown_json,
        'branch_appointments': branch_appointments,
        'staff_performance': staff_performance,
        'total_inventory_value': total_inventory_value,
        'expiring_products': expiring_products,
        'pet_species_breakdown': pet_species_breakdown,
        'pet_species_breakdown_json': pet_species_breakdown_json,
        'appointment_sources': appointment_sources,
        'appointment_sources_json': appointment_sources_json,
        'revenue_growth': revenue_growth,
        'cancellation_rate': cancellation_rate,
        'new_patients_this_week': new_patients_this_week,
        'new_customers_this_week': new_customers_this_week,
        'returning_customers_this_week': returning_customers_this_week,
        'service_breakdown': service_breakdown,
        'payment_method_stats': payment_method_stats_list,
        'payment_method_stats_json': payment_method_stats_json,
        'pet_health_stats': pet_health_stats,
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
        'refunds_today': refunds_today,
        'total_revenue_this_week': total_revenue_this_week,
    })


@login_required
@module_permission_required('dashboard')
def vet_dashboard_view(request):
    """Veterinarian-specific dashboard with comprehensive statistics."""
    from appointments.models import Appointment
    from patients.models import Pet
    from employees.models import StaffMember, VetSchedule
    from notifications.models import Notification, FollowUp
    from records.models import MedicalRecord

    today = date.today()
    week_end = today + timedelta(days=7)
    month_start = date(today.year, today.month, 1)

    # Get the vet's staff profile
    try:
        staff_profile = request.user.staff_profile
    except StaffMember.DoesNotExist:
        staff_profile = None

    # ── Total assigned patients (get distinct pets from vet's appointments) ──
    if staff_profile:
        assigned_patients = Pet.objects.filter(
            appointments__preferred_vet=staff_profile
        ).distinct().count()
    else:
        assigned_patients = 0

    # ── Today's appointments for this vet ──
    if staff_profile:
        todays_appointments = Appointment.objects.filter(
            appointment_date=today,
            preferred_vet=staff_profile,
            pet__isnull=False,
        ).exclude(status='CANCELLED').select_related('pet', 'branch').order_by('appointment_time')
    else:
        todays_appointments = Appointment.objects.none()

    today_count = todays_appointments.count()

    # ── Upcoming appointments (next 7 days) ──
    if staff_profile:
        upcoming_appointments = Appointment.objects.filter(
            appointment_date__gt=today,
            appointment_date__lte=week_end,
            preferred_vet=staff_profile,
            pet__isnull=False,
        ).exclude(status='CANCELLED').select_related('pet', 'branch').order_by('appointment_date', 'appointment_time')
    else:
        upcoming_appointments = Appointment.objects.none()

    upcoming_count = upcoming_appointments.count()

    # ── Completed consultations (past appointments with status COMPLETED) ──
    if staff_profile:
        completed_consultations = Appointment.objects.filter(
            preferred_vet=staff_profile,
            status='COMPLETED',
            pet__isnull=False,
        ).count()
    else:
        completed_consultations = 0

    # ── Medical records created by this vet ──
    if staff_profile:
        medical_records_count = MedicalRecord.objects.filter(
            vet=staff_profile
        ).count()
    else:
        medical_records_count = 0

    # ── Pending follow-ups for this vet's patients ──
    if staff_profile:
        follow_ups = FollowUp.objects.filter(
            appointment__preferred_vet=staff_profile,
            is_completed=False,
            follow_up_date__gte=today,
        ).select_related('appointment', 'appointment__pet').order_by('follow_up_date')[:10]
    else:
        follow_ups = FollowUp.objects.none()

    follow_up_count = follow_ups.count()

    # ── This week's schedule ──
    if staff_profile:
        this_week_schedule = VetSchedule.objects.filter(
            staff=staff_profile,
            date__gte=today,
            date__lte=week_end,
        ).select_related('branch').order_by('date', 'start_time')
    else:
        this_week_schedule = VetSchedule.objects.none()

    # ── Unread notifications ──
    unread_notif_count = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()

    # ─── COMPREHENSIVE ANALYTICS ───

    # Patient status distribution
    if staff_profile:
        patient_status_distribution = Pet.objects.filter(
            appointments__preferred_vet=staff_profile
        ).distinct().values('status').annotate(count=Count('id')).order_by('-count')
    else:
        patient_status_distribution = []

    # Consultation reasons breakdown
    if staff_profile:
        consultation_reasons_query = Appointment.objects.filter(
            preferred_vet=staff_profile,
            pet__isnull=False
        ).values('reason').annotate(count=Count('id')).order_by('-count')
        
        # Convert to list and calculate percentages
        consultation_reasons = list(consultation_reasons_query)
        if consultation_reasons:
            max_count = consultation_reasons[0]['count'] or 1
            for reason in consultation_reasons:
                reason['percentage'] = (reason['count'] / max_count * 100) if max_count > 0 else 0
    else:
        consultation_reasons = []

    # Average daily consultations (last 30 days)
    if staff_profile:
        consultations_last_30_days = Appointment.objects.filter(
            preferred_vet=staff_profile,
            appointment_date__range=[today - timedelta(days=30), today],
            status='COMPLETED',
            pet__isnull=False
        ).count()
        avg_daily_consultations = consultations_last_30_days / 30 if consultations_last_30_days > 0 else 0
    else:
        avg_daily_consultations = 0

    # New vs returning patients (this month)
    if staff_profile:
        new_patients_this_month = Pet.objects.filter(
            appointments__preferred_vet=staff_profile,
            created_at__date__range=[month_start, today]
        ).distinct().count()

        returning_patients_this_month = Appointment.objects.filter(
            preferred_vet=staff_profile,
            appointment_date__range=[month_start, today],
            is_returning_customer=True,
            pet__isnull=False
        ).values('pet').distinct().count()
    else:
        new_patients_this_month = 0
        returning_patients_this_month = 0

    # Surgeries count (this month)
    if staff_profile:
        surgeries_this_month = Appointment.objects.filter(
            preferred_vet=staff_profile,
            appointment_date__range=[month_start, today],
            reason=Appointment.Reason.SURGERY,
            pet__isnull=False
        ).count()
    else:
        surgeries_this_month = 0

    # Emergency cases count
    if staff_profile:
        emergency_cases = Appointment.objects.filter(
            preferred_vet=staff_profile,
            reason=Appointment.Reason.EMERGENCY,
            pet__isnull=False
        ).count()
    else:
        emergency_cases = 0

    # Vaccinations count
    if staff_profile:
        vaccinations_count = Appointment.objects.filter(
            preferred_vet=staff_profile,
            reason=Appointment.Reason.VACCINATION,
            pet__isnull=False
        ).count()
    else:
        vaccinations_count = 0

    # Medical records created this month
    if staff_profile:
        medical_records_this_month = MedicalRecord.objects.filter(
            vet=staff_profile,
            date_recorded__range=[month_start, today]
        ).count()
    else:
        medical_records_this_month = 0

    return render(request, 'accounts/vet_dashboard.html', {
        'staff_profile': staff_profile,
        'assigned_patients': assigned_patients,
        'today_count': today_count,
        'todays_appointments': todays_appointments[:10],
        'upcoming_count': upcoming_count,
        'upcoming_appointments': upcoming_appointments[:10],
        'completed_consultations': completed_consultations,
        'medical_records_count': medical_records_count,
        'follow_up_count': follow_up_count,
        'follow_ups': follow_ups,
        'this_week_schedule': this_week_schedule,
        'unread_notif_count': unread_notif_count,
        'patient_status_distribution': patient_status_distribution,
        'consultation_reasons': consultation_reasons,
        'avg_daily_consultations': avg_daily_consultations,
        'new_patients_this_month': new_patients_this_month,
        'returning_patients_this_month': returning_patients_this_month,
        'surgeries_this_month': surgeries_this_month,
        'emergency_cases': emergency_cases,
        'vaccinations_count': vaccinations_count,
        'medical_records_this_month': medical_records_this_month,
    })


@login_required
@module_permission_required('dashboard')
def receptionist_dashboard_view(request):
    """Receptionist-specific dashboard with POS, appointments, and customer management focus."""
    from appointments.models import Appointment
    from patients.models import Pet
    from pos.models import Sale, Payment
    from billing.models import CustomerStatement
    from notifications.models import Notification

    today = date.today()
    yesterday = today - timedelta(days=1)
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    # ── Today's appointments ──
    todays_appointments = Appointment.objects.filter(
        appointment_date=today,
        pet__isnull=False,
    ).select_related('branch', 'preferred_vet').order_by('appointment_time')

    today_count = todays_appointments.count()
    today_confirmed = todays_appointments.filter(status='CONFIRMED').count()
    today_pending = todays_appointments.filter(status='PENDING').count()

    # ── Today's sales statistics ──
    todays_sales = Sale.objects.filter(
        created_at__date=today,
        status='COMPLETED'
    )
    todays_sales_count = todays_sales.count()
    todays_revenue = sum(sale.total for sale in todays_sales) if todays_sales else 0

    # ── This week's statistics ──
    weekly_sales = Sale.objects.filter(
        created_at__date__range=[week_start, week_end],
        status='COMPLETED'
    )
    weekly_sales_count = weekly_sales.count()
    weekly_revenue = sum(sale.total for sale in weekly_sales) if weekly_sales else 0

    # ── Pending tasks ──
    pending_appointments = Appointment.objects.filter(
        status='PENDING',
        appointment_date__gte=today
    ).count()

    draft_statements = CustomerStatement.objects.filter(status='DRAFT').count()

    # ── Recent sales ──
    recent_sales = Sale.objects.filter(
        status__in=['COMPLETED', 'REFUNDED']
    ).select_related('customer', 'pet').order_by('-created_at')[:5]

    # ── Upcoming appointments (next 3 days) ──
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__range=[today + timedelta(days=1), today + timedelta(days=3)],
        pet__isnull=False
    ).select_related('branch', 'preferred_vet').order_by('appointment_date', 'appointment_time')[:10]

    # ── Recent registrations (new pets this week) ──
    new_pets_this_week = Pet.objects.filter(
        created_at__range=[week_start, week_end]
    ).count()

    # ── Unread notifications ──
    unread_notif_count = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()

    # ── Statement statistics ──
    total_statements = CustomerStatement.objects.count()
    released_statements = CustomerStatement.objects.filter(status__in=['RELEASED', 'SENT']).count()

    # ─── COMPREHENSIVE ANALYTICS ───

    # Walk-in vs Portal appointments (today)
    walkin_today = Appointment.objects.filter(
        appointment_date=today,
        source='WALKIN',
        pet__isnull=False
    ).count()
    portal_today = Appointment.objects.filter(
        appointment_date=today,
        source='PORTAL',
        pet__isnull=False
    ).count()

    # Hourly distribution of appointments (today)
    hourly_distribution = Appointment.objects.filter(
        appointment_date=today,
        pet__isnull=False
    ).values('appointment_time__hour').annotate(
        count=Count('id')
    ).order_by('appointment_time__hour')

    # Registered vs Walk-in sales (today)
    registered_sales_today = Sale.objects.filter(
        created_at__date=today,
        customer_type='REGISTERED',
        status='COMPLETED'
    ).aggregate(total=Sum('total'))['total'] or 0

    walkin_sales_today = Sale.objects.filter(
        created_at__date=today,
        customer_type='WALKIN',
        status='COMPLETED'
    ).aggregate(total=Sum('total'))['total'] or 0

    # Refunds today with amount
    refunds_today = Sale.objects.filter(
        created_at__date=today,
        status='REFUNDED'
    )
    refunds_count = refunds_today.count()
    refunds_amount = sum(sale.total for sale in refunds_today) if refunds_today else 0

    # Pending reservations
    pending_reservations = Appointment.objects.filter(
        appointment_date__gte=today,
        status='PENDING',
        pet__isnull=False
    ).count()

    # Appointment by reason breakdown (today)
    appointment_reasons_today_query = Appointment.objects.filter(
        appointment_date=today,
        pet__isnull=False
    ).values('reason').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Convert to list and calculate percentages
    appointment_reasons_today = list(appointment_reasons_today_query)
    if appointment_reasons_today:
        max_count = appointment_reasons_today[0]['count'] or 1
        for reason in appointment_reasons_today:
            reason['percentage'] = (reason['count'] / max_count * 100) if max_count > 0 else 0

    # Revenue comparison vs yesterday
    yesterdays_revenue = Sale.objects.filter(
        created_at__date=yesterday,
        status='COMPLETED'
    ).aggregate(total=Sum('total'))['total'] or 0

    revenue_diff = float(todays_revenue) - float(yesterdays_revenue)
    revenue_diff_pct = (
        (revenue_diff / yesterdays_revenue * 100)
        if yesterdays_revenue > 0 else 0
    )

    # Payment method breakdown
    payment_method_breakdown_query = Payment.objects.filter(
        sale__created_at__date=today,
        sale__status='COMPLETED'
    ).values('method').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-count')
    
    # Convert to list and calculate percentages
    payment_method_breakdown = list(payment_method_breakdown_query)
    if payment_method_breakdown:
        max_count = payment_method_breakdown[0]['count'] or 1
        for method in payment_method_breakdown:
            method['percentage'] = (method['count'] / max_count * 100) if max_count > 0 else 0

    # Check-in statistics (today)
    checked_in_today = Appointment.objects.filter(
        appointment_date=today,
        status='COMPLETED',
        pet__isnull=False
    ).count()

    context = {
        # Appointment stats
        'today_count': today_count,
        'today_confirmed': today_confirmed,
        'today_pending': today_pending,
        'pending_appointments': pending_appointments,
        'pending_reservations': pending_reservations,

        # Sales stats
        'todays_sales_count': todays_sales_count,
        'todays_revenue': todays_revenue,
        'weekly_sales_count': weekly_sales_count,
        'weekly_revenue': weekly_revenue,
        'registered_sales_today': registered_sales_today,
        'walkin_sales_today': walkin_sales_today,

        # Customer stats
        'new_pets_this_week': new_pets_this_week,
        'total_statements': total_statements,
        'released_statements': released_statements,
        'draft_statements': draft_statements,

        # Recent activity
        'todays_appointments': todays_appointments[:10],
        'upcoming_appointments': upcoming_appointments,
        'recent_sales': recent_sales,

        # Notifications
        'unread_notif_count': unread_notif_count,

        # Additional analytics
        'walkin_today': walkin_today,
        'portal_today': portal_today,
        'hourly_distribution': hourly_distribution,
        'refunds_count': refunds_count,
        'refunds_amount': refunds_amount,
        'appointment_reasons_today': appointment_reasons_today,
        'yesterdays_revenue': yesterdays_revenue,
        'revenue_diff': revenue_diff,
        'revenue_diff_pct': revenue_diff_pct,
        'payment_method_breakdown': payment_method_breakdown,
        'checked_in_today': checked_in_today,
    }

    return render(request, 'accounts/receptionist_dashboard.html', context)


@login_required
@admin_only
@module_permission_required('staff', 'CREATE')
def admin_create_account(request):
    """Admin view to create new staff accounts (not Pet Owners).
    
    Staff accounts must be created through this form. Pet Owners register
    themselves via the public registration page.
    """
    from .forms import AdminAccountCreationForm

    if request.method == 'POST':
        form = AdminAccountCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Auto-create StaffMember if staff role assigned
            if user.assigned_role and user.assigned_role.is_staff_role:
                from employees.models import StaffMember
                # Map RBAC role to StaffMember position
                role_to_position = {
                    'veterinarian': StaffMember.Position.VETERINARIAN,
                    'vet_assistant': StaffMember.Position.VET_ASSISTANT,
                    'receptionist': StaffMember.Position.RECEPTIONIST,
                    'branch_admin': StaffMember.Position.ADMIN,
                    'superadmin': StaffMember.Position.ADMIN,
                    'admin': StaffMember.Position.ADMIN,
                }
                position = role_to_position.get(
                    user.assigned_role.code,
                    StaffMember.Position.RECEPTIONIST
                )

                # Create or update StaffMember record
                StaffMember.objects.update_or_create(
                    user=user,
                    defaults={
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'phone': user.phone_number or '',
                        'position': position,
                        'branch': user.branch,
                        'is_active': True,
                    }
                )

            messages.success(request, f'Account created for {user.get_full_name() or user.username}.')
            return redirect('accounts:user_role_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminAccountCreationForm()

    return render(request, 'accounts/admin_create_account.html', {'form': form})
