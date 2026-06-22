"""
Hospital Receptionist AI Agent - Handles patient registration, triage, and routing.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class ReceptionistAI:
    """
    Hospital Receptionist AI Agent.
    
    This agent handles:
    - Patient registration
    - Chief complaint recording
    - Department routing
    - Appointment scheduling
    - Basic guidance provision
    
    Note: This is a modular implementation ready for LLM integration
    (Gemini, OpenAI, etc.) in future iterations.
    """
    
    # Department mapping based on symptoms/complaints
    DEPARTMENT_MAP = {
        'fever': 'General Medicine',
        'chest pain': 'Cardiology',
        'headache': 'Neurology',
        'cough': 'Pulmonology',
        'stomach': 'Gastroenterology',
        'joint': 'Orthopedics',
        'skin': 'Dermatology',
        'eye': 'Ophthalmology',
        'ear': 'Otolaryngology',
        'psychiatric': 'Psychiatry',
        'injury': 'Trauma & Emergency',
        'dental': 'Dentistry',
        'women': 'Obstetrics & Gynecology',
        'child': 'Pediatrics',
        'mental': 'Psychiatry',
        'depression': 'Psychiatry',
        'anxiety': 'Psychiatry',
    }
    
    # Triage levels
    TRIAGE_LEVELS = {
        'critical': 1,
        'urgent': 2,
        'moderate': 3,
        'mild': 4,
    }
    
    # Critical symptoms requiring immediate attention
    CRITICAL_SYMPTOMS = [
        'chest pain',
        'difficulty breathing',
        'unconscious',
        'severe bleeding',
        'poisoning',
        'severe allergic reaction',
        'stroke symptoms',
    ]
    
    # Department availability (mock data - can be integrated with real scheduling system)
    DEPARTMENT_AVAILABILITY = {
        'General Medicine': True,
        'Cardiology': True,
        'Neurology': True,
        'Pulmonology': False,
        'Gastroenterology': True,
        'Orthopedics': True,
        'Dermatology': True,
        'Ophthalmology': False,
        'Otolaryngology': True,
        'Psychiatry': True,
        'Trauma & Emergency': True,
        'Pediatrics': True,
    }
    
    def __init__(self):
        """Initialize the Receptionist AI Agent."""
        self.llm_provider = None  # Can be set to 'gemini', 'openai', etc.
        self.model_name = None
    
    def set_llm_provider(self, provider: str, api_key: str = None):
        """
        Configure the LLM provider for enhanced AI capabilities.
        
        Args:
            provider (str): LLM provider ('gemini', 'openai', etc.)
            api_key (str): API key for the provider
        """
        self.llm_provider = provider
        # In future: Initialize actual LLM client
    
    def get_available_departments(self) -> List[Dict]:
        """
        Get list of available departments.
        
        Returns:
            List[Dict]: List of department information
        """
        departments = []
        for dept, available in self.DEPARTMENT_AVAILABILITY.items():
            departments.append({
                'name': dept,
                'available': available,
                'wait_time': '15 mins' if available else 'Closed'
            })
        return departments
    
    def assess_triage(self, chief_complaint: str, symptoms: List[str] = None) -> Dict:
        """
        Assess patient triage level based on chief complaint and symptoms.
        
        Args:
            chief_complaint (str): Patient's chief complaint
            symptoms (List[str]): List of symptoms
        
        Returns:
            Dict: Triage assessment with priority level and guidance
        """
        complaint_lower = chief_complaint.lower()
        
        # Check for critical symptoms
        for critical in self.CRITICAL_SYMPTOMS:
            if critical in complaint_lower:
                return {
                    'priority': 'critical',
                    'priority_level': 1,
                    'guidance': 'URGENT: Patient requires immediate medical attention. Direct to Emergency Department immediately.',
                    'estimated_wait': '< 5 minutes'
                }
        
        # Assess based on complaint
        if any(word in complaint_lower for word in ['severe', 'unbearable', 'emergency', 'acute']):
            return {
                'priority': 'urgent',
                'priority_level': 2,
                'guidance': 'Patient requires urgent attention. Direct to appropriate specialist department.',
                'estimated_wait': '15-30 minutes'
            }
        
        if any(word in complaint_lower for word in ['mild', 'slight', 'minor']):
            return {
                'priority': 'mild',
                'priority_level': 4,
                'guidance': 'Patient can be scheduled for routine consultation.',
                'estimated_wait': '1-2 hours'
            }
        
        # Default to moderate
        return {
            'priority': 'moderate',
            'priority_level': 3,
            'guidance': 'Patient requires specialist consultation.',
            'estimated_wait': '30-60 minutes'
        }
    
    def recommend_department(self, chief_complaint: str, reason_for_visit: str = None) -> str:
        """
        Recommend appropriate department for patient.
        
        Args:
            chief_complaint (str): Chief complaint
            reason_for_visit (str): Detailed reason for visit
        
        Returns:
            str: Recommended department name
        """
        search_text = (chief_complaint + ' ' + (reason_for_visit or '')).lower()
        
        # Find best matching department
        for symptom, department in self.DEPARTMENT_MAP.items():
            if symptom in search_text:
                return department
        
        # Default to General Medicine
        return 'General Medicine'
    
    def check_appointment_availability(self, department: str) -> Dict:
        """
        Check appointment availability for a department.
        
        Args:
            department (str): Department name
        
        Returns:
            Dict: Availability information
        """
        available = self.DEPARTMENT_AVAILABILITY.get(department, False)
        
        if available:
            # Generate mock appointment slots
            slots = []
            base_time = datetime.now() + timedelta(days=1)
            for i in range(4):
                slot_time = base_time + timedelta(hours=i*2)
                slots.append(slot_time.isoformat())
            
            return {
                'available': True,
                'next_available': slots[0],
                'available_slots': slots,
                'estimated_wait': '2-3 days for routine appointment'
            }
        else:
            return {
                'available': False,
                'message': f'{department} is currently closed or at capacity.',
                'alternative_department': 'General Medicine'
            }
    
    def get_appointment_guidance(self, department: str) -> str:
        """
        Get appointment guidance for a specific department.
        
        Args:
            department (str): Department name
        
        Returns:
            str: Guidance text for appointment
        """
        guidance_map = {
            'Cardiology': 'Please bring any previous ECG reports. Appointment typically takes 45 minutes.',
            'Orthopedics': 'Wear comfortable, loose clothing. Bring X-rays if available.',
            'Psychiatry': 'First appointment typically takes 60 minutes. Please be prepared to discuss medical history.',
            'Trauma & Emergency': 'You will be seen immediately based on severity assessment.',
        }
        
        return guidance_map.get(department, f'Please arrive 15 minutes early for your {department} appointment.')
    
    def generate_appointment_confirmation(self, appointment) -> str:
        """
        Generate appointment confirmation message.
        
        Args:
            appointment: Appointment object
        
        Returns:
            str: Confirmation message
        """
        return (
            f"Appointment Confirmation\n"
            f"Department: {appointment.department}\n"
            f"Date & Time: {appointment.appointment_date.strftime('%B %d, %Y at %I:%M %p')}\n"
            f"Reason: {appointment.reason}\n"
            f"Status: {appointment.status}\n"
            f"Please arrive 15 minutes early."
        )
    
    def provide_guidance(self, patient) -> str:
        """
        Provide guidance to a patient based on their information.
        
        Args:
            patient: Patient object
        
        Returns:
            str: Guidance text
        """
        guidance_parts = []
        
        # Welcome
        guidance_parts.append(f"Welcome, {patient.first_name}!")
        
        # Allergy warning
        if patient.allergies:
            guidance_parts.append(f"\n⚠️ Allergies on File: {patient.allergies}")
        
        # Medication info
        if patient.current_medications:
            guidance_parts.append(f"\n📋 Current Medications: {patient.current_medications}")
        
        # Department assignment
        if patient.assigned_department:
            dept = patient.assigned_department
            guidance_parts.append(f"\n📍 Please proceed to: {dept} Department")
            guidance_parts.append(f"   {self.get_appointment_guidance(dept)}")
        
        # Additional instructions
        guidance_parts.append("\n✓ Please have your insurance card ready")
        guidance_parts.append("✓ Notify staff immediately if you experience chest pain or difficulty breathing")
        
        return ''.join(guidance_parts)
    
    def record_chief_complaint(self, patient, chief_complaint: str, reason_for_visit: str = None) -> Dict:
        """
        Record patient's chief complaint and reason for visit.
        
        Args:
            patient: Patient object
            chief_complaint (str): Chief complaint
            reason_for_visit (str): Reason for visit
        
        Returns:
            Dict: Recording confirmation with analysis
        """
        # This would update the patient record in actual implementation
        return {
            'success': True,
            'chief_complaint_recorded': chief_complaint,
            'department_recommendation': self.recommend_department(chief_complaint, reason_for_visit),
            'next_step': 'Please proceed to the recommended department for consultation.'
        }
