"""
Database models for the I-HIS application.
"""
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.icu import VitalSign, ClinicalAlert

__all__ = ['Patient', 'Appointment', 'VitalSign', 'ClinicalAlert']
