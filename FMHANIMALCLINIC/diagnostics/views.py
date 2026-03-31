"""
Views for the AI Diagnostics module.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from django.core.paginator import Paginator
from accounts.decorators import module_permission_required
from appointments.models import Appointment
from patients.models import Pet
from records.models import RecordEntry

from .models import AIDiagnosis
from .services import get_ai_diagnosis


@login_required
@module_permission_required('ai_diagnostics', 'VIEW')
def dashboard(request):
    """AI Diagnostics dashboard - list pets, recent diagnoses."""
    # Get recent diagnoses
    recent_diagnoses = AIDiagnosis.objects.select_related(
        'pet', 'requested_by'
    ).order_by('-created_at')[:20]

    # Get active pets for quick access
    pets_query = Pet.objects.filter(is_active=True).select_related('owner')

    # Search functionality
    search = request.GET.get('search', '').strip()
    if search:
        pets_query = pets_query.filter(
            name__icontains=search
        ).order_by('name')
    else:
        pets_query = pets_query.order_by('-created_at')

    # Pagination
    paginator = Paginator(pets_query, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'recent_diagnoses': recent_diagnoses,
        'pets': page_obj.object_list,
        'page_obj': page_obj,
        'search': search,
    }
    return render(request, 'diagnostics/dashboard.html', context)


@login_required
@module_permission_required('ai_diagnostics', 'CREATE')
def run_diagnosis(request, pet_id):
    """Run AI diagnosis for a specific pet."""
    pet = get_object_or_404(Pet, pk=pet_id)

    # Get medical history
    entries = RecordEntry.objects.filter(
        record__pet=pet
    ).select_related('record').order_by('-date_recorded')

    # Get latest appointment with symptoms
    latest_appointment = Appointment.objects.filter(
        pet=pet
    ).order_by('-appointment_date', '-created_at').first()

    # Get previous diagnoses for this pet
    previous_diagnoses = AIDiagnosis.objects.filter(
        pet=pet
    ).order_by('-created_at')[:5]

    if request.method == 'POST':
        # Get additional symptoms from form
        additional_symptoms = request.POST.get('additional_symptoms', '').strip()

        # Run AI diagnosis
        result = get_ai_diagnosis(
            pet=pet,
            record_entries=entries,
            appointment=latest_appointment,
            additional_symptoms=additional_symptoms if additional_symptoms else None
        )

        # Get staff profile if available
        staff_member = None
        if hasattr(request.user, 'staff_profile'):
            staff_member = request.user.staff_profile

        # Save to database
        diagnosis = AIDiagnosis.objects.create(
            pet=pet,
            requested_by=staff_member,
            input_symptoms=additional_symptoms or (
                latest_appointment.pet_symptoms if latest_appointment else ''
            ),
            input_history=result.get('_input_history', ''),
            primary_condition=result.get('primary_diagnosis', {}).get('condition', 'Unknown'),
            primary_reasoning=result.get('primary_diagnosis', {}).get('reasoning', ''),
            differential_diagnoses=result.get('differential_diagnoses', []),
            recommended_tests=result.get('recommended_tests', []),
            warning_signs=result.get('warning_signs', []),
            summary=result.get('summary', ''),
            raw_response=result.get('_raw', None)
        )

        messages.success(request, f'AI diagnosis completed for {pet.name}.')
        return redirect('diagnostics:detail', pk=diagnosis.pk)

    context = {
        'pet': pet,
        'entries': entries[:10],
        'latest_appointment': latest_appointment,
        'previous_diagnoses': previous_diagnoses,
        'has_history': entries.exists(),
    }
    return render(request, 'diagnostics/run_diagnosis.html', context)


@login_required
@module_permission_required('ai_diagnostics', 'VIEW')
def diagnosis_detail(request, pk):
    """View a specific AI diagnosis result."""
    diagnosis = get_object_or_404(
        AIDiagnosis.objects.select_related('pet', 'requested_by', 'reviewed_by'),
        pk=pk
    )

    # Get other diagnoses for the same pet
    related_diagnoses = AIDiagnosis.objects.filter(
        pet=diagnosis.pet
    ).exclude(pk=pk).order_by('-created_at')[:5]

    context = {
        'diagnosis': diagnosis,
        'related_diagnoses': related_diagnoses,
    }
    return render(request, 'diagnostics/detail.html', context)


@login_required
@module_permission_required('ai_diagnostics', 'VIEW')
def pet_diagnosis_history(request, pet_id):
    """View all AI diagnoses for a pet (JSON API)."""
    pet = get_object_or_404(Pet, pk=pet_id)

    diagnoses = AIDiagnosis.objects.filter(pet=pet).order_by('-created_at')[:20]

    data = {
        'pet': {
            'id': pet.id,
            'name': pet.name,
        },
        'diagnoses': [
            {
                'id': d.id,
                'primary_condition': d.primary_condition,
                'summary': d.summary,
                'created_at': d.created_at.isoformat(),
                'is_reviewed': d.is_reviewed,
            }
            for d in diagnoses
        ]
    }
    return JsonResponse(data)


@login_required
@module_permission_required('ai_diagnostics', 'VIEW')
@require_http_methods(['POST'])
def mark_reviewed(request, pk):
    """Mark a diagnosis as reviewed by the veterinarian."""
    from django.utils import timezone

    diagnosis = get_object_or_404(AIDiagnosis, pk=pk)

    staff_member = None
    if hasattr(request.user, 'staff_profile'):
        staff_member = request.user.staff_profile

    diagnosis.is_reviewed = True
    diagnosis.reviewed_by = staff_member
    diagnosis.reviewed_at = timezone.now()
    diagnosis.review_notes = request.POST.get('review_notes', '')
    diagnosis.save()

    messages.success(request, 'Diagnosis marked as reviewed.')
    return redirect('diagnostics:detail', pk=pk)
