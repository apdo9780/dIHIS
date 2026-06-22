"""
Patient management routes for the I-HIS application.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app import db
from app.models import Patient, Appointment
from app.forms import PatientRegistrationForm, PatientSearchForm
from sqlalchemy import or_
import uuid
from datetime import datetime

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')


def generate_mrn():
    """Generate a unique Medical Record Number (MRN)."""
    # Format: I-HIS-XXXXXX (e.g., I-HIS-ABC123)
    unique_id = str(uuid.uuid4())[:6].upper()
    return f'I-HIS-{unique_id}'


@patient_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Patient registration route."""
    form = PatientRegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Generate unique MRN
            mrn = generate_mrn()
            
            # Create new patient record
            patient = Patient(
                mrn=mrn,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                date_of_birth=form.date_of_birth.data,
                gender=form.gender.data,
                email=form.email.data or None,
                phone=form.phone.data,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                postal_code=form.postal_code.data,
                country=form.country.data,
                emergency_contact_name=form.emergency_contact_name.data,
                emergency_contact_phone=form.emergency_contact_phone.data,
                medical_history=form.medical_history.data or None,
                allergies=form.allergies.data or None,
                current_medications=form.current_medications.data or None,
                chief_complaint=form.chief_complaint.data or None,
                reason_for_visit=form.reason_for_visit.data or None,
            )
            
            db.session.add(patient)
            db.session.commit()
            
            flash(f'Patient successfully registered! MRN: {mrn}', 'success')
            return redirect(url_for('patient.view_patient', patient_id=patient.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering patient: {str(e)}', 'danger')
    
    return render_template('patient/register.html', form=form)


@patient_bp.route('/view/<int:patient_id>')
def view_patient(patient_id):
    """View patient EPR."""
    patient = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    return render_template('patient/epr.html', patient=patient, appointments=appointments)


@patient_bp.route('/search', methods=['GET', 'POST'])
def search():
    """Search for patients."""
    form = PatientSearchForm()
    results = []
    
    if form.validate_on_submit():
        query = form.search_query.data
        results = Patient.query.filter(
            or_(
                Patient.mrn.ilike(f'%{query}%'),
                Patient.first_name.ilike(f'%{query}%'),
                Patient.last_name.ilike(f'%{query}%'),
                Patient.email.ilike(f'%{query}%'),
            )
        ).all()
        
        if not results:
            flash('No patients found.', 'info')
    
    return render_template('patient/search.html', form=form, results=results)


@patient_bp.route('/edit/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    """Edit patient information."""
    patient = Patient.query.get_or_404(patient_id)
    form = PatientRegistrationForm()
    
    if form.validate_on_submit():
        try:
            patient.first_name = form.first_name.data
            patient.last_name = form.last_name.data
            patient.date_of_birth = form.date_of_birth.data
            patient.gender = form.gender.data
            patient.email = form.email.data or None
            patient.phone = form.phone.data
            patient.address = form.address.data
            patient.city = form.city.data
            patient.state = form.state.data
            patient.postal_code = form.postal_code.data
            patient.country = form.country.data
            patient.emergency_contact_name = form.emergency_contact_name.data
            patient.emergency_contact_phone = form.emergency_contact_phone.data
            patient.medical_history = form.medical_history.data or None
            patient.allergies = form.allergies.data or None
            patient.current_medications = form.current_medications.data or None
            patient.chief_complaint = form.chief_complaint.data or None
            patient.reason_for_visit = form.reason_for_visit.data or None
            
            db.session.commit()
            flash('Patient information updated successfully!', 'success')
            return redirect(url_for('patient.view_patient', patient_id=patient.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating patient: {str(e)}', 'danger')
    
    elif request.method == 'GET':
        form.first_name.data = patient.first_name
        form.last_name.data = patient.last_name
        form.date_of_birth.data = patient.date_of_birth
        form.gender.data = patient.gender
        form.email.data = patient.email
        form.phone.data = patient.phone
        form.address.data = patient.address
        form.city.data = patient.city
        form.state.data = patient.state
        form.postal_code.data = patient.postal_code
        form.country.data = patient.country
        form.emergency_contact_name.data = patient.emergency_contact_name
        form.emergency_contact_phone.data = patient.emergency_contact_phone
        form.medical_history.data = patient.medical_history
        form.allergies.data = patient.allergies
        form.current_medications.data = patient.current_medications
        form.chief_complaint.data = patient.chief_complaint
        form.reason_for_visit.data = patient.reason_for_visit
    
    return render_template('patient/edit.html', form=form, patient=patient)


@patient_bp.route('/api/patient/<int:patient_id>')
def api_get_patient(patient_id):
    """API endpoint to get patient data as JSON."""
    patient = Patient.query.get_or_404(patient_id)
    return jsonify(patient.to_dict())


@patient_bp.route('/api/search')
def api_search():
    """API endpoint for patient search."""
    query = request.args.get('q', '')
    results = Patient.query.filter(
        or_(
            Patient.mrn.ilike(f'%{query}%'),
            Patient.first_name.ilike(f'%{query}%'),
            Patient.last_name.ilike(f'%{query}%'),
        )
    ).limit(10).all()
    
    return jsonify([{
        'id': p.id,
        'mrn': p.mrn,
        'name': p.full_name
    } for p in results])
