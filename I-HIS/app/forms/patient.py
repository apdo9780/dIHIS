"""
Forms for patient registration and management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.fields import DateField, EmailField, TelField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp, ValidationError
from app.models import Patient


class PatientRegistrationForm(FlaskForm):
    """Form for registering a new patient."""
    
    # Personal Information
    first_name = StringField(
        'First Name',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'placeholder': 'Enter first name', 'class': 'form-control'}
    )
    
    last_name = StringField(
        'Last Name',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'placeholder': 'Enter last name', 'class': 'form-control'}
    )
    
    date_of_birth = DateField(
        'Date of Birth',
        validators=[DataRequired()],
        render_kw={'class': 'form-control'}
    )
    
    gender = SelectField(
        'Gender',
        choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        validators=[DataRequired()],
        render_kw={'class': 'form-control'}
    )
    
    # Contact Information
    email = EmailField(
        'Email Address',
        validators=[Optional(), Email()],
        render_kw={'placeholder': 'example@email.com', 'class': 'form-control'}
    )
    
    phone = TelField(
        'Phone Number',
        validators=[DataRequired(), Length(min=10, max=20)],
        render_kw={'placeholder': '+1 (555) 123-4567', 'class': 'form-control'}
    )
    
    # Address Information
    address = StringField(
        'Street Address',
        validators=[DataRequired(), Length(min=5, max=255)],
        render_kw={'placeholder': 'Enter street address', 'class': 'form-control'}
    )
    
    city = StringField(
        'City',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'placeholder': 'Enter city', 'class': 'form-control'}
    )
    
    state = StringField(
        'State/Province',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'placeholder': 'Enter state', 'class': 'form-control'}
    )
    
    postal_code = StringField(
        'Postal Code',
        validators=[DataRequired(), Length(min=3, max=20)],
        render_kw={'placeholder': 'Enter postal code', 'class': 'form-control'}
    )
    
    country = StringField(
        'Country',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'placeholder': 'Enter country', 'class': 'form-control'}
    )
    
    # Emergency Contact
    emergency_contact_name = StringField(
        'Emergency Contact Name',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'placeholder': 'Name of emergency contact', 'class': 'form-control'}
    )
    
    emergency_contact_phone = TelField(
        'Emergency Contact Phone',
        validators=[DataRequired(), Length(min=10, max=20)],
        render_kw={'placeholder': 'Emergency contact phone', 'class': 'form-control'}
    )
    
    # Medical Information
    medical_history = TextAreaField(
        'Medical History',
        validators=[Optional()],
        render_kw={'placeholder': 'Enter any relevant medical history...', 'class': 'form-control', 'rows': '4'}
    )
    
    allergies = TextAreaField(
        'Known Allergies',
        validators=[Optional()],
        render_kw={'placeholder': 'List any known allergies...', 'class': 'form-control', 'rows': '3'}
    )
    
    current_medications = TextAreaField(
        'Current Medications',
        validators=[Optional()],
        render_kw={'placeholder': 'List current medications...', 'class': 'form-control', 'rows': '3'}
    )
    
    # Visit Information
    chief_complaint = StringField(
        'Chief Complaint',
        validators=[Optional(), Length(max=255)],
        render_kw={'placeholder': 'Main reason for visit', 'class': 'form-control'}
    )
    
    reason_for_visit = TextAreaField(
        'Reason for Visit',
        validators=[Optional()],
        render_kw={'placeholder': 'Detailed reason for this visit...', 'class': 'form-control', 'rows': '4'}
    )
    
    submit = SubmitField(
        'Register Patient',
        render_kw={'class': 'btn btn-primary w-100'}
    )
    
    def validate_email(self, field):
        """Check if email is already registered."""
        if field.data and Patient.query.filter_by(email=field.data).first():
            raise ValidationError('This email is already registered.')


class PatientSearchForm(FlaskForm):
    """Form for searching patients."""
    
    search_query = StringField(
        'Search by Name or MRN',
        validators=[DataRequired(), Length(min=2)],
        render_kw={'placeholder': 'Enter patient name or MRN...', 'class': 'form-control'}
    )
    
    submit = SubmitField(
        'Search',
        render_kw={'class': 'btn btn-info'}
    )
