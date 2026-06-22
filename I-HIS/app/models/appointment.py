"""
Appointment model for managing patient appointments.
"""
from datetime import datetime
from app import db


class Appointment(db.Model):
    """
    Appointment model representing scheduled appointments.
    
    Attributes:
        id (int): Unique appointment identifier
        patient_id (int): Foreign key to patient
        appointment_date (datetime): Scheduled appointment date and time
        department (str): Healthcare department for appointment
        reason (str): Reason for appointment
        status (str): Appointment status (scheduled, completed, cancelled, no-show)
        notes (str): Additional notes about appointment
        created_at (datetime): Record creation timestamp
    """
    
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    appointment_date = db.Column(db.DateTime, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='scheduled')
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Appointment {self.id}: {self.patient_id} - {self.appointment_date}>'
    
    def to_dict(self):
        """Convert appointment to dictionary."""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'appointment_date': self.appointment_date.isoformat(),
            'department': self.department,
            'reason': self.reason,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
        }
