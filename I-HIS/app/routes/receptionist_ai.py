"""
Hospital Receptionist AI routes for patient routing and appointment scheduling.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.ai_agents import ReceptionistAI
from app import db
from app.models import Patient, Appointment
from datetime import datetime

receptionist_bp = Blueprint('receptionist', __name__, url_prefix='/receptionist')
receptionist_ai = ReceptionistAI()


@receptionist_bp.route('/interface')
def interface():
    """Receptionist AI interface."""
    departments = receptionist_ai.get_available_departments()
    return render_template('receptionist/interface.html', departments=departments)


@receptionist_bp.route('/api/register-patient', methods=['POST'])
def api_register_patient():
    """API endpoint for AI-assisted patient registration."""
    data = request.get_json()
    
    try:
        # Extract patient information
        patient_data = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'phone': data.get('phone'),
            'chief_complaint': data.get('chief_complaint'),
            'reason_for_visit': data.get('reason_for_visit'),
        }
        
        # Validate required fields
        if not all([patient_data['first_name'], patient_data['last_name'], patient_data['phone']]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        # Get AI recommendation for department
        department_recommendation = receptionist_ai.recommend_department(
            chief_complaint=patient_data['chief_complaint'],
            reason_for_visit=patient_data['reason_for_visit']
        )
        
        response = {
            'success': True,
            'message': 'Patient information collected successfully',
            'recommended_department': department_recommendation,
            'next_steps': f'Please direct patient to {department_recommendation} department.',
            'appointment_guidance': receptionist_ai.get_appointment_guidance(department_recommendation)
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@receptionist_bp.route('/api/triage-patient', methods=['POST'])
def api_triage_patient():
    """API endpoint for AI-assisted patient triage."""
    data = request.get_json()
    
    try:
        patient_id = data.get('patient_id')
        chief_complaint = data.get('chief_complaint')
        symptoms = data.get('symptoms', [])
        
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'message': 'Patient not found'}), 404
        
        # Get AI triage assessment
        triage_result = receptionist_ai.assess_triage(
            chief_complaint=chief_complaint,
            symptoms=symptoms
        )
        
        # Get department routing
        department = receptionist_ai.recommend_department(
            chief_complaint=chief_complaint,
            reason_for_visit=', '.join(symptoms) if symptoms else ''
        )
        
        # Update patient record
        patient.chief_complaint = chief_complaint
        patient.reason_for_visit = ', '.join(symptoms) if symptoms else ''
        patient.assigned_department = department
        db.session.commit()
        
        response = {
            'success': True,
            'patient_id': patient_id,
            'triage_level': triage_result['priority'],
            'assigned_department': department,
            'guidance': triage_result['guidance'],
            'appointment_available': receptionist_ai.check_appointment_availability(department)
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@receptionist_bp.route('/api/schedule-appointment', methods=['POST'])
def api_schedule_appointment():
    """API endpoint for appointment scheduling."""
    data = request.get_json()
    
    try:
        patient_id = data.get('patient_id')
        appointment_date = data.get('appointment_date')
        department = data.get('department')
        reason = data.get('reason')
        
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'message': 'Patient not found'}), 404
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            appointment_date=datetime.fromisoformat(appointment_date),
            department=department,
            reason=reason,
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        response = {
            'success': True,
            'message': 'Appointment scheduled successfully',
            'appointment_id': appointment.id,
            'confirmation': receptionist_ai.generate_appointment_confirmation(appointment)
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@receptionist_bp.route('/api/get-guidance/<int:patient_id>')
def api_get_guidance(patient_id):
    """API endpoint to get guidance for a patient."""
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'success': False, 'message': 'Patient not found'}), 404
    
    guidance = receptionist_ai.provide_guidance(patient)
    
    return jsonify({
        'success': True,
        'guidance': guidance
    }), 200
