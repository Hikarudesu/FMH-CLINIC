"""
AI Diagnostic Service using GROQ API.

This module provides the integration with GROQ's LLM API to analyze
pet medical records and suggest potential diagnoses.
"""
import json
import logging
from datetime import date

from django.conf import settings

logger = logging.getLogger('fmh')


def get_ai_diagnosis(pet, record_entries, appointment=None, additional_symptoms=None):
    """
    Analyze pet medical records using GROQ API.

    Args:
        pet: Pet model instance
        record_entries: QuerySet of RecordEntry objects
        appointment: Optional latest Appointment with pet_symptoms
        additional_symptoms: Optional string with additional symptoms to analyze

    Returns:
        dict with diagnosis data
    """
    try:
        from groq import Groq
    except ImportError:
        logger.error("GROQ package not installed. Run: pip install groq")
        return _error_response("GROQ package not installed")

    api_key = getattr(settings, 'GROQ_API_KEY', None)
    if not api_key:
        logger.error("GROQ_API_KEY not configured in settings")
        return _error_response("API key not configured")

    try:
        groq_client = Groq(api_key=api_key)

        # Build pet info
        pet_info = build_pet_info(pet)

        # Build history text
        history_text = build_history_text(record_entries)

        # Include appointment symptoms if available
        if appointment and appointment.pet_symptoms:
            history_text = f"Current presenting symptoms (from appointment): {appointment.pet_symptoms}\n\n{history_text}"

        # Include additional symptoms if provided
        if additional_symptoms:
            history_text = f"Current symptoms being analyzed: {additional_symptoms}\n\n{history_text}"

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": """Role: You are a Veterinary Diagnostic Assistant AI.

Task: Analyze the pet's medical history and clinical signs to:
1. Identify potential diagnoses based on current symptoms
2. Flag concerning patterns or symptoms
3. Suggest follow-up tests or examinations if needed
4. Predict potential future health concerns based on history

Output ONLY a valid JSON object with this structure:
{
    "primary_diagnosis": {
        "condition": "string - most likely condition",
        "reasoning": "string - brief explanation"
    },
    "differential_diagnoses": [
        {"condition": "string", "reasoning": "string"}
    ],
    "recommended_tests": ["list of suggested tests"],
    "warning_signs": ["symptoms to monitor"],
    "summary": "string - brief overall assessment"
}

Important:
- Be conservative with diagnoses
- Always recommend professional veterinary confirmation
- Consider species-specific conditions
- Note if insufficient data for diagnosis
- Maximum 3 differential diagnoses
- Maximum 5 recommended tests
- Maximum 5 warning signs"""
                },
                {
                    "role": "user",
                    "content": f"Pet Information:\n{pet_info}\n\nMedical History:\n{history_text}"
                }
            ]
        )

        result = parse_groq_response(response.choices[0].message.content)
        result['_raw'] = response.choices[0].message.content
        result['_input_pet_info'] = pet_info
        result['_input_history'] = history_text
        return result

    except Exception as e:
        logger.exception(f"GROQ API error: {e}")
        return _error_response(str(e))


def build_pet_info(pet):
    """Build pet information string."""
    age = calculate_age(pet.date_of_birth)
    return f"""Name: {pet.name}
Species: {pet.species or 'Unknown'}
Breed: {pet.breed or 'Unknown'}
Age: {age}
Sex: {pet.get_sex_display() if hasattr(pet, 'get_sex_display') else pet.sex}
Current Clinical Status: {pet.get_status_display() if hasattr(pet, 'get_status_display') else pet.status}"""


def build_history_text(entries):
    """Convert RecordEntry queryset to formatted text."""
    if not entries or (hasattr(entries, 'exists') and not entries.exists()):
        return "No prior medical history available."

    parts = []
    for entry in entries[:10]:  # Limit to last 10 entries to avoid token limits
        parts.append(f"""Date: {entry.date_recorded}
Vitals: Weight {entry.weight or 'N/A'}kg, Temp {entry.temperature or 'N/A'}C
Clinical Signs: {entry.history_clinical_signs or 'None recorded'}
Treatment: {entry.treatment or 'None'}
Prescription: {entry.rx or 'None'}
Status: {entry.action_required}
---""")
    return "\n".join(parts)


def calculate_age(dob):
    """Calculate age from date of birth."""
    if not dob:
        return "Unknown"
    today = date.today()
    years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if years < 1:
        months = (today.year - dob.year) * 12 + today.month - dob.month
        if months < 1:
            return "Less than 1 month"
        return f"{months} month{'s' if months > 1 else ''}"
    return f"{years} year{'s' if years > 1 else ''}"


def parse_groq_response(content):
    """Parse GROQ response JSON safely."""
    try:
        data = json.loads(content)
        # Validate expected structure
        if 'primary_diagnosis' not in data:
            return _error_response("Invalid response structure")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse GROQ response: {e}")
        return _error_response("Could not parse AI response")


def _error_response(error_message):
    """Return a standardized error response."""
    return {
        "primary_diagnosis": {
            "condition": "Unable to determine",
            "reasoning": error_message
        },
        "differential_diagnoses": [],
        "recommended_tests": [],
        "warning_signs": [],
        "summary": f"The AI was unable to provide a diagnosis. Error: {error_message}. Please consult with a veterinarian.",
        "_error": True
    }
