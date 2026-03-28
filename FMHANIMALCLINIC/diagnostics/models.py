from django.db import models
from patients.models import Pet
from employees.models import StaffMember


class AIDiagnosis(models.Model):
    """Stores AI-generated diagnostic suggestions for a pet."""

    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name='ai_diagnoses'
    )
    requested_by = models.ForeignKey(
        StaffMember,
        on_delete=models.SET_NULL,
        null=True,
        related_name='requested_diagnoses'
    )

    # Input data snapshot
    input_symptoms = models.TextField(
        help_text="Symptoms provided for analysis",
        blank=True
    )
    input_history = models.TextField(
        help_text="Medical history snapshot",
        blank=True
    )

    # AI Response - Primary Diagnosis
    primary_condition = models.CharField(max_length=200)
    primary_reasoning = models.TextField(blank=True)

    # AI Response - Additional Data (stored as JSON)
    differential_diagnoses = models.JSONField(
        default=list,
        help_text="List of {condition, reasoning}"
    )
    recommended_tests = models.JSONField(default=list)
    warning_signs = models.JSONField(default=list)
    summary = models.TextField(blank=True)

    # Raw response for debugging
    raw_response = models.JSONField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        StaffMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_diagnoses'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Diagnosis'
        verbose_name_plural = 'AI Diagnoses'

    def __str__(self):
        return f"{self.pet.name} - {self.primary_condition} ({self.created_at.date()})"
