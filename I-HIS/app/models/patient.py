"""
Patient model for Electronic Patient Record (EPR) storage.
"""
from datetime import datetime
from app import db


class Patient(db.Model):
    """
    Patient model representing a patient's electronic health record.
    
    Attributes:
        id (int): Unique patient identifier
        mrn (str): Medical Record Number (unique identifier)
        first_name (str): Patient's first name
        last_name (str): Patient's last name
        date_of_birth (date): Patient's date of birth
        gender (str): Patient's gender
        email (str): Patient's email address
        phone (str): Patient's phone number
        address (str): Patient's residential address
        city (str): City of residence
        state (str): State of residence
        postal_code (str): Postal code
        country (str): Country of residence
        emergency_contact_name (str): Emergency contact person name
        emergency_contact_phone (str): Emergency contact phone number
        medical_history (str): Patient's medical history notes
        allergies (str): Known allergies
        current_medications (str): Current medications list
        chief_complaint (str): Chief complaint for current visit
        reason_for_visit (str): Detailed reason for visit
        assigned_department (str): Assigned healthcare department
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp
        status (str): Patient status (active, inactive, archived)
    """
    
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Personal Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    
    # Contact Information
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(20), nullable=False)
    
    # Address Information
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100), nullable=False)
    emergency_contact_phone = db.Column(db.String(20), nullable=False)
    
    # Medical Information
    medical_history = db.Column(db.Text, nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    current_medications = db.Column(db.Text, nullable=True)
    
    # Visit Information
    chief_complaint = db.Column(db.String(255), nullable=True)
    reason_for_visit = db.Column(db.Text, nullable=True)
    assigned_department = db.Column(db.String(100), nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='active')
    
    # Relationship
    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Patient {self.mrn}: {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        """Return patient's full name."""
        return f'{self.first_name} {self.last_name}'
    
    @property
    def age(self):
        """Calculate patient's age from date of birth."""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def to_dict(self):
        """Convert patient record to dictionary."""
        return {
            'id': self.id,
            'mrn': self.mrn,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat(),
            'age': self.age,
            'gender': self.gender,
            'email': self.email,
            'phone': self.phone,
            'address': f'{self.address}, {self.city}, {self.state} {self.postal_code}',
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'medical_history': self.medical_history,
            'allergies': self.allergies,
            'current_medications': self.current_medications,
            'chief_complaint': self.chief_complaint,
            'reason_for_visit': self.reason_for_visit,
            'assigned_department': self.assigned_department,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
