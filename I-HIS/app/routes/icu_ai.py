"""
ICU Specialist AI Routes - Clinical Decision Support System.

Provides dashboard for ICU monitoring and API endpoints for vital sign data
ingestion and clinical alert generation.
"""
from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta
from app import db
from app.models import Patient, VitalSign, ClinicalAlert
from app.ai_agents import ICUSpecialistAI

# Initialize blueprint
icu_bp = Blueprint('icu', __name__, url_prefix='/icu')

# Initialize AI agent
icu_ai = ICUSpecialistAI()


@icu_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Render ICU monitoring dashboard with live clinical alerts and vital signs.
    
    Fetches:
    - All unacknowledged clinical alerts
    - Latest vital signs for ICU patients
    - Patient information for context
    
    Returns:
        Rendered dashboard template with alert and vital data
    """
    try:
        # Fetch all unacknowledged alerts
        unacknowledged_alerts = ClinicalAlert.query.filter_by(
            is_acknowledged=False
        ).order_by(ClinicalAlert.created_at.desc()).all()
        
        # Fetch critical alerts for prominence
        critical_alerts = ClinicalAlert.query.filter_by(
            is_acknowledged=False,
            alert_level='Critical'
        ).order_by(ClinicalAlert.created_at.desc()).all()
        
        # Get patients with recent vital signs (last 1 hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_vitals = VitalSign.query.filter(
            VitalSign.recorded_at >= one_hour_ago
        ).all()
        
        # Organize vitals by patient
        patient_vitals = {}
        for vital in recent_vitals:
            if vital.patient_id not in patient_vitals:
                patient = Patient.query.get(vital.patient_id)
                patient_vitals[vital.patient_id] = {
                    'patient': patient,
                    'vitals': []
                }
            patient_vitals[vital.patient_id]['vitals'].append(vital)
        
        # Get latest vital per patient
        latest_patient_vitals = []
        for patient_id, data in patient_vitals.items():
            if data['vitals']:
                latest = max(data['vitals'], key=lambda v: v.recorded_at)
                latest_patient_vitals.append({
                    'patient': data['patient'],
                    'vital': latest
                })
        
        return render_template(
            'icu/dashboard.html',
            unacknowledged_alerts=unacknowledged_alerts,
            critical_alerts=critical_alerts,
            alert_count=len(unacknowledged_alerts),
            critical_count=len(critical_alerts),
            patient_vitals=latest_patient_vitals
        )
    
    except Exception as e:
        return render_template(
            'icu/dashboard.html',
            error=f"Error loading dashboard: {str(e)}",
            unacknowledged_alerts=[],
            critical_alerts=[],
            alert_count=0,
            critical_count=0,
            patient_vitals=[]
        )


@icu_bp.route('/api/vitals', methods=['POST'])
def record_vitals():
    """
    API endpoint for recording patient vital signs and generating clinical alerts.
    
    Expected JSON payload:
    {
        'patient_id': int (required),
        'heart_rate': int,
        'blood_pressure_systolic': int,
        'blood_pressure_diastolic': int,
        'oxygen_saturation': float (0-100),
        'temperature': float (Celsius),
        'respiratory_rate': int
    }
    
    Returns:
        JSON response with:
        - success: bool
        - vital_sign_id: int (if successful)
        - alerts_generated: list
        - message: str
    """
    try:
        data = request.get_json()
        
        # Validate required patient_id
        patient_id = data.get('patient_id')
        if not patient_id:
            return jsonify({
                'success': False,
                'message': 'patient_id is required'
            }), 400
        
        # Verify patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({
                'success': False,
                'message': f'Patient with ID {patient_id} not found'
            }), 404
        
        # Create vital sign record
        vital_sign = VitalSign(
            patient_id=patient_id,
            heart_rate=data.get('heart_rate'),
            blood_pressure_systolic=data.get('blood_pressure_systolic'),
            blood_pressure_diastolic=data.get('blood_pressure_diastolic'),
            oxygen_saturation=data.get('oxygen_saturation'),
            temperature=data.get('temperature'),
            respiratory_rate=data.get('respiratory_rate'),
            recorded_at=datetime.fromisoformat(data.get('recorded_at', datetime.utcnow().isoformat()))
        )
        
        db.session.add(vital_sign)
        db.session.flush()  # Flush to get vital_sign.id
        
        # Evaluate vitals using AI
        vital_data = {
            'heart_rate': vital_sign.heart_rate,
            'blood_pressure_systolic': vital_sign.blood_pressure_systolic,
            'blood_pressure_diastolic': vital_sign.blood_pressure_diastolic,
            'oxygen_saturation': vital_sign.oxygen_saturation,
            'temperature': vital_sign.temperature,
            'respiratory_rate': vital_sign.respiratory_rate
        }
        
        evaluation = icu_ai.evaluate_vitals(vital_data)
        
        # Generate alerts if abnormalities detected
        alerts_generated = []
        if not evaluation['is_normal']:
            alerts = icu_ai.generate_alerts(evaluation)
            
            for alert in alerts:
                clinical_alert = ClinicalAlert(
                    patient_id=patient_id,
                    alert_level=alert['alert_level'],
                    message=alert['message'],
                    recommended_intervention=alert['recommended_intervention'],
                    vital_sign_id=vital_sign.id,
                    is_acknowledged=False
                )
                db.session.add(clinical_alert)
                alerts_generated.append(alert)
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'vital_sign_id': vital_sign.id,
            'vital_sign': vital_sign.to_dict(),
            'evaluation': {
                'is_normal': evaluation['is_normal'],
                'overall_severity': evaluation['overall_severity'],
                'abnormalities': evaluation['abnormalities']
            },
            'alerts_generated': alerts_generated,
            'alert_count': len(alerts_generated),
            'message': f'Vital signs recorded. {len(alerts_generated)} alert(s) generated.' if alerts_generated else 'Vital signs recorded. All parameters normal.'
        }), 201
    
    except ValueError as ve:
        return jsonify({
            'success': False,
            'message': f'Invalid data format: {str(ve)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error recording vital signs: {str(e)}'
        }), 500


@icu_bp.route('/api/alerts', methods=['GET'])
def get_alerts():
    """
    API endpoint for fetching clinical alerts.
    
    Query parameters:
    - acknowledged (bool): Filter by acknowledgment status (default: False)
    - patient_id (int): Filter by specific patient (optional)
    - alert_level (str): Filter by alert level ('Warning', 'Critical') (optional)
    - limit (int): Maximum records to return (default: 50)
    
    Returns:
        JSON array of alert objects
    """
    try:
        # Build query
        query = ClinicalAlert.query
        
        # Filter by acknowledgment status (default to unacknowledged)
        acknowledged = request.args.get('acknowledged', 'false').lower() == 'true'
        query = query.filter_by(is_acknowledged=acknowledged)
        
        # Filter by patient_id if provided
        patient_id = request.args.get('patient_id')
        if patient_id:
            query = query.filter_by(patient_id=int(patient_id))
        
        # Filter by alert_level if provided
        alert_level = request.args.get('alert_level')
        if alert_level in ['Warning', 'Critical']:
            query = query.filter_by(alert_level=alert_level)
        
        # Order by creation time (newest first)
        query = query.order_by(ClinicalAlert.created_at.desc())
        
        # Limit results
        limit = int(request.args.get('limit', 50))
        alerts = query.limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(alerts),
            'alerts': [alert.to_dict() for alert in alerts]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching alerts: {str(e)}'
        }), 500


@icu_bp.route('/api/alerts/<int:alert_id>/acknowledge', methods=['PUT', 'PATCH'])
def acknowledge_alert(alert_id):
    """
    API endpoint to acknowledge a clinical alert.
    
    Expected JSON payload (optional):
    {
        'acknowledged_by': str (clinician identifier)
    }
    
    Returns:
        JSON response with updated alert object
    """
    try:
        alert = ClinicalAlert.query.get(alert_id)
        if not alert:
            return jsonify({
                'success': False,
                'message': f'Alert {alert_id} not found'
            }), 404
        
        data = request.get_json() or {}
        acknowledged_by = data.get('acknowledged_by', 'System')
        
        alert.acknowledge(acknowledged_by)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'alert': alert.to_dict(),
            'message': f'Alert {alert_id} acknowledged'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error acknowledging alert: {str(e)}'
        }), 500


@icu_bp.route('/api/vitals/<int:patient_id>', methods=['GET'])
def get_patient_vitals(patient_id):
    """
    API endpoint for fetching patient vital signs.
    
    Query parameters:
    - hours (int): Fetch vitals from past N hours (default: 24)
    - limit (int): Maximum records to return (default: 100)
    
    Returns:
        JSON array of vital sign objects
    """
    try:
        # Verify patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({
                'success': False,
                'message': f'Patient {patient_id} not found'
            }), 404
        
        # Calculate time window
        hours = int(request.args.get('hours', 24))
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Fetch vitals
        limit = int(request.args.get('limit', 100))
        vitals = VitalSign.query.filter(
            VitalSign.patient_id == patient_id,
            VitalSign.recorded_at >= time_threshold
        ).order_by(VitalSign.recorded_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'patient_name': f"{patient.first_name} {patient.last_name}",
            'mrn': patient.mrn,
            'count': len(vitals),
            'time_window_hours': hours,
            'vitals': [vital.to_dict() for vital in vitals]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching patient vitals: {str(e)}'
        }), 500


@icu_bp.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """
    API endpoint for fetching all dashboard data (alerts + vitals).
    Used by JavaScript polling for real-time dashboard updates.
    
    Returns:
        JSON object with alerts, vitals, and summary statistics
    """
    try:
        # Fetch unacknowledged alerts
        unacknowledged_alerts = ClinicalAlert.query.filter_by(
            is_acknowledged=False
        ).order_by(ClinicalAlert.created_at.desc()).all()
        
        # Fetch critical alerts
        critical_alerts = ClinicalAlert.query.filter_by(
            is_acknowledged=False,
            alert_level='Critical'
        ).all()
        
        # Get recent vitals (last 30 minutes)
        thirty_min_ago = datetime.utcnow() - timedelta(minutes=30)
        recent_vitals = VitalSign.query.filter(
            VitalSign.recorded_at >= thirty_min_ago
        ).order_by(VitalSign.recorded_at.desc()).all()
        
        # Get unique patients with recent vitals
        patient_ids = set(v.patient_id for v in recent_vitals)
        patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
        
        # Build response
        return jsonify({
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_alerts': len(unacknowledged_alerts),
                'critical_alerts': len(critical_alerts),
                'warning_alerts': len(unacknowledged_alerts) - len(critical_alerts),
                'patients_monitored': len(patients),
                'recent_vitals_count': len(recent_vitals)
            },
            'critical_alerts': [alert.to_dict() for alert in critical_alerts],
            'warning_alerts': [alert.to_dict() for alert in unacknowledged_alerts if alert.alert_level == 'Warning'],
            'recent_patients': [
                {
                    'patient_id': p.id,
                    'mrn': p.mrn,
                    'name': f"{p.first_name} {p.last_name}",
                    'department': p.assigned_department
                }
                for p in patients
            ]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching dashboard data: {str(e)}'
        }), 500
