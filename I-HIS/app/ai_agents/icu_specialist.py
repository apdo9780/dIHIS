"""
ICU Specialist AI Agent - Clinical Decision Support System (CDSS).

This module provides intelligent monitoring of patient vital signs and
generates clinical alerts based on evidence-based medical thresholds.
Designed for modular expansion to integrate LLM providers in future iterations.
"""
from typing import Dict, List, Optional, Tuple


class ICUSpecialistAI:
    """
    Intelligent ICU monitoring and clinical decision support agent.
    
    This agent:
    - Evaluates vital signs against medical thresholds
    - Detects critical conditions
    - Generates clinical alerts with recommended interventions
    - Provides evidence-based decision support
    
    Note: Intentionally separated from database layer for pure business logic
    and testability. Database operations should occur in route handlers.
    """
    
    # Medical thresholds for abnormal vital signs
    # Based on standard clinical guidelines
    NORMAL_RANGES = {
        'heart_rate': {'min': 60, 'max': 100},
        'systolic_bp': {'min': 90, 'max': 140},
        'diastolic_bp': {'min': 60, 'max': 90},
        'oxygen_saturation': {'min': 95, 'max': 100},  # Room air
        'temperature': {'min': 36.5, 'max': 37.5},
        'respiratory_rate': {'min': 12, 'max': 20}
    }
    
    # Critical thresholds requiring immediate intervention
    CRITICAL_THRESHOLDS = {
        'heart_rate_critical_low': 40,
        'heart_rate_critical_high': 140,
        'systolic_bp_critical_low': 80,
        'diastolic_bp_critical_high': 110,
        'oxygen_saturation_critical': 85,
        'temperature_critical_high': 40,
        'temperature_critical_low': 35,
        'respiratory_rate_critical_low': 8,
        'respiratory_rate_critical_high': 30
    }
    
    def __init__(self):
        """Initialize ICU Specialist AI agent."""
        self.last_evaluation = None
        self.alert_history = []
    
    def evaluate_vitals(self, vital_data: Dict) -> Dict:
        """
        Evaluate patient vital signs against medical thresholds.
        
        Args:
            vital_data (dict): Dictionary containing:
                - heart_rate (int): BPM
                - blood_pressure_systolic (int): mmHg
                - blood_pressure_diastolic (int): mmHg
                - oxygen_saturation (float): % (0-100)
                - temperature (float): Celsius
                - respiratory_rate (int): breaths/min
        
        Returns:
            dict: Evaluation results with findings and abnormalities
                {
                    'is_normal': bool,
                    'abnormalities': [
                        {
                            'parameter': str,
                            'value': float,
                            'severity': 'Warning' or 'Critical',
                            'status': 'Low', 'High', or 'Abnormal'
                        }
                    ],
                    'overall_severity': 'Normal', 'Warning', or 'Critical',
                    'vital_data': dict (input data)
                }
        """
        abnormalities = []
        overall_severity = 'Normal'
        
        # Evaluate Heart Rate
        hr = vital_data.get('heart_rate')
        if hr is not None:
            hr_eval = self._evaluate_heart_rate(hr)
            if hr_eval:
                abnormalities.append(hr_eval)
                if hr_eval['severity'] == 'Critical':
                    overall_severity = 'Critical'
                elif overall_severity != 'Critical':
                    overall_severity = 'Warning'
        
        # Evaluate Blood Pressure
        systolic = vital_data.get('blood_pressure_systolic')
        diastolic = vital_data.get('blood_pressure_diastolic')
        if systolic is not None or diastolic is not None:
            bp_eval = self._evaluate_blood_pressure(systolic, diastolic)
            if bp_eval:
                abnormalities.extend(bp_eval)
                for finding in bp_eval:
                    if finding['severity'] == 'Critical':
                        overall_severity = 'Critical'
                    elif overall_severity != 'Critical':
                        overall_severity = 'Warning'
        
        # Evaluate Oxygen Saturation
        spo2 = vital_data.get('oxygen_saturation')
        if spo2 is not None:
            spo2_eval = self._evaluate_oxygen_saturation(spo2)
            if spo2_eval:
                abnormalities.append(spo2_eval)
                if spo2_eval['severity'] == 'Critical':
                    overall_severity = 'Critical'
                elif overall_severity != 'Critical':
                    overall_severity = 'Warning'
        
        # Evaluate Temperature
        temp = vital_data.get('temperature')
        if temp is not None:
            temp_eval = self._evaluate_temperature(temp)
            if temp_eval:
                abnormalities.append(temp_eval)
                if temp_eval['severity'] == 'Critical':
                    overall_severity = 'Critical'
                elif overall_severity != 'Critical':
                    overall_severity = 'Warning'
        
        # Evaluate Respiratory Rate
        rr = vital_data.get('respiratory_rate')
        if rr is not None:
            rr_eval = self._evaluate_respiratory_rate(rr)
            if rr_eval:
                abnormalities.append(rr_eval)
                if rr_eval['severity'] == 'Critical':
                    overall_severity = 'Critical'
                elif overall_severity != 'Critical':
                    overall_severity = 'Warning'
        
        self.last_evaluation = {
            'is_normal': len(abnormalities) == 0,
            'abnormalities': abnormalities,
            'overall_severity': overall_severity,
            'vital_data': vital_data
        }
        
        return self.last_evaluation
    
    def _evaluate_heart_rate(self, hr: int) -> Optional[Dict]:
        """Evaluate heart rate for abnormalities."""
        if hr < self.CRITICAL_THRESHOLDS['heart_rate_critical_low']:
            return {
                'parameter': 'Heart Rate',
                'value': hr,
                'unit': 'BPM',
                'severity': 'Critical',
                'status': 'Critically Low',
                'reference_range': f"{self.NORMAL_RANGES['heart_rate']['min']}-{self.NORMAL_RANGES['heart_rate']['max']}"
            }
        elif hr > self.CRITICAL_THRESHOLDS['heart_rate_critical_high']:
            return {
                'parameter': 'Heart Rate',
                'value': hr,
                'unit': 'BPM',
                'severity': 'Critical',
                'status': 'Critically High',
                'reference_range': f"{self.NORMAL_RANGES['heart_rate']['min']}-{self.NORMAL_RANGES['heart_rate']['max']}"
            }
        elif hr < self.NORMAL_RANGES['heart_rate']['min'] or hr > self.NORMAL_RANGES['heart_rate']['max']:
            return {
                'parameter': 'Heart Rate',
                'value': hr,
                'unit': 'BPM',
                'severity': 'Warning',
                'status': 'Low' if hr < self.NORMAL_RANGES['heart_rate']['min'] else 'High',
                'reference_range': f"{self.NORMAL_RANGES['heart_rate']['min']}-{self.NORMAL_RANGES['heart_rate']['max']}"
            }
        return None
    
    def _evaluate_blood_pressure(self, systolic: Optional[int], diastolic: Optional[int]) -> List[Dict]:
        """Evaluate blood pressure for abnormalities."""
        findings = []
        
        if systolic is not None:
            if systolic < self.CRITICAL_THRESHOLDS['systolic_bp_critical_low']:
                findings.append({
                    'parameter': 'Systolic Blood Pressure',
                    'value': systolic,
                    'unit': 'mmHg',
                    'severity': 'Critical',
                    'status': 'Critically Low (Hypotension)',
                    'reference_range': f"{self.NORMAL_RANGES['systolic_bp']['min']}-{self.NORMAL_RANGES['systolic_bp']['max']}"
                })
            elif systolic > self.NORMAL_RANGES['systolic_bp']['max']:
                findings.append({
                    'parameter': 'Systolic Blood Pressure',
                    'value': systolic,
                    'unit': 'mmHg',
                    'severity': 'Warning',
                    'status': 'Elevated',
                    'reference_range': f"{self.NORMAL_RANGES['systolic_bp']['min']}-{self.NORMAL_RANGES['systolic_bp']['max']}"
                })
        
        if diastolic is not None:
            if diastolic > self.CRITICAL_THRESHOLDS['diastolic_bp_critical_high']:
                findings.append({
                    'parameter': 'Diastolic Blood Pressure',
                    'value': diastolic,
                    'unit': 'mmHg',
                    'severity': 'Warning',
                    'status': 'Elevated',
                    'reference_range': f"{self.NORMAL_RANGES['diastolic_bp']['min']}-{self.NORMAL_RANGES['diastolic_bp']['max']}"
                })
        
        return findings
    
    def _evaluate_oxygen_saturation(self, spo2: float) -> Optional[Dict]:
        """Evaluate oxygen saturation for abnormalities."""
        if spo2 < self.CRITICAL_THRESHOLDS['oxygen_saturation_critical']:
            return {
                'parameter': 'Oxygen Saturation (SpO2)',
                'value': spo2,
                'unit': '%',
                'severity': 'Critical',
                'status': 'Critically Low',
                'reference_range': f"{self.NORMAL_RANGES['oxygen_saturation']['min']}-{self.NORMAL_RANGES['oxygen_saturation']['max']}"
            }
        elif spo2 < self.NORMAL_RANGES['oxygen_saturation']['min']:
            return {
                'parameter': 'Oxygen Saturation (SpO2)',
                'value': spo2,
                'unit': '%',
                'severity': 'Warning',
                'status': 'Low',
                'reference_range': f"{self.NORMAL_RANGES['oxygen_saturation']['min']}-{self.NORMAL_RANGES['oxygen_saturation']['max']}"
            }
        return None
    
    def _evaluate_temperature(self, temp: float) -> Optional[Dict]:
        """Evaluate temperature for abnormalities."""
        if temp > self.CRITICAL_THRESHOLDS['temperature_critical_high']:
            return {
                'parameter': 'Temperature',
                'value': temp,
                'unit': '°C',
                'severity': 'Critical',
                'status': 'Critically High (Hyperthermia)',
                'reference_range': f"{self.NORMAL_RANGES['temperature']['min']}-{self.NORMAL_RANGES['temperature']['max']}"
            }
        elif temp < self.CRITICAL_THRESHOLDS['temperature_critical_low']:
            return {
                'parameter': 'Temperature',
                'value': temp,
                'unit': '°C',
                'severity': 'Critical',
                'status': 'Critically Low (Hypothermia)',
                'reference_range': f"{self.NORMAL_RANGES['temperature']['min']}-{self.NORMAL_RANGES['temperature']['max']}"
            }
        elif temp < self.NORMAL_RANGES['temperature']['min'] or temp > self.NORMAL_RANGES['temperature']['max']:
            return {
                'parameter': 'Temperature',
                'value': temp,
                'unit': '°C',
                'severity': 'Warning',
                'status': 'Abnormal',
                'reference_range': f"{self.NORMAL_RANGES['temperature']['min']}-{self.NORMAL_RANGES['temperature']['max']}"
            }
        return None
    
    def _evaluate_respiratory_rate(self, rr: int) -> Optional[Dict]:
        """Evaluate respiratory rate for abnormalities."""
        if rr < self.CRITICAL_THRESHOLDS['respiratory_rate_critical_low']:
            return {
                'parameter': 'Respiratory Rate',
                'value': rr,
                'unit': 'breaths/min',
                'severity': 'Critical',
                'status': 'Critically Low (Bradypnea)',
                'reference_range': f"{self.NORMAL_RANGES['respiratory_rate']['min']}-{self.NORMAL_RANGES['respiratory_rate']['max']}"
            }
        elif rr > self.CRITICAL_THRESHOLDS['respiratory_rate_critical_high']:
            return {
                'parameter': 'Respiratory Rate',
                'value': rr,
                'unit': 'breaths/min',
                'severity': 'Critical',
                'status': 'Critically High (Tachypnea)',
                'reference_range': f"{self.NORMAL_RANGES['respiratory_rate']['min']}-{self.NORMAL_RANGES['respiratory_rate']['max']}"
            }
        elif rr < self.NORMAL_RANGES['respiratory_rate']['min'] or rr > self.NORMAL_RANGES['respiratory_rate']['max']:
            return {
                'parameter': 'Respiratory Rate',
                'value': rr,
                'unit': 'breaths/min',
                'severity': 'Warning',
                'status': 'Abnormal',
                'reference_range': f"{self.NORMAL_RANGES['respiratory_rate']['min']}-{self.NORMAL_RANGES['respiratory_rate']['max']}"
            }
        return None
    
    def generate_alerts(self, evaluation_results: Dict) -> List[Dict]:
        """
        Generate clinical alerts based on vital sign evaluation.
        
        Args:
            evaluation_results (dict): Output from evaluate_vitals()
        
        Returns:
            list: List of alert dictionaries
                [
                    {
                        'alert_level': 'Warning' or 'Critical',
                        'message': str,
                        'recommended_intervention': str,
                        'affected_parameters': [str]
                    }
                ]
        """
        alerts = []
        
        if not evaluation_results['abnormalities']:
            return alerts
        
        abnormalities = evaluation_results['abnormalities']
        
        # Group abnormalities by parameter for contextual alerts
        critical_abnormalities = [a for a in abnormalities if a['severity'] == 'Critical']
        warning_abnormalities = [a for a in abnormalities if a['severity'] == 'Warning']
        
        # Generate Critical Alerts
        if critical_abnormalities:
            parameters = [a['parameter'] for a in critical_abnormalities]
            
            # Determine intervention based on critical findings
            if any('Heart Rate' in p and 'Low' in str(a['status']) for p, a in [(a['parameter'], a) for a in critical_abnormalities]):
                alerts.append({
                    'alert_level': 'Critical',
                    'message': 'Severe Bradycardia Detected - Heart rate critically low',
                    'recommended_intervention': 'Immediate intervention required. Notify physician immediately. Assess for AV block, medication overdose, or cardiac ischemia. Consider atropine or pacing if symptomatic.',
                    'affected_parameters': parameters
                })
            
            if any('Heart Rate' in p and 'High' in str(a['status']) for p, a in [(a['parameter'], a) for a in critical_abnormalities]):
                alerts.append({
                    'alert_level': 'Critical',
                    'message': 'Severe Tachycardia Detected - Heart rate critically high',
                    'recommended_intervention': 'Immediate evaluation required. Notify physician. Assess for sepsis, shock, hyperthyroidism, or cardiac arrhythmia. Obtain 12-lead ECG.',
                    'affected_parameters': parameters
                })
            
            if any('Systolic Blood Pressure' in p and 'Low' in str(a['status']) for p, a in [(a['parameter'], a) for a in critical_abnormalities]):
                alerts.append({
                    'alert_level': 'Critical',
                    'message': 'Severe Hypotension Detected - Systolic BP critically low',
                    'recommended_intervention': 'EMERGENCY - Initiate vasopressor support. Notify physician and intensivist. Assess for shock state. Increase IV fluids. Check for active bleeding or sepsis.',
                    'affected_parameters': parameters
                })
            
            if any('Oxygen Saturation' in p for p in parameters):
                alerts.append({
                    'alert_level': 'Critical',
                    'message': 'Severe Hypoxemia Detected - SpO2 critically low',
                    'recommended_intervention': 'EMERGENCY - Initiate oxygen therapy immediately. Notify respiratory therapy and physician. Check oxygen delivery device. Prepare for intubation if SpO2 remains <85%.',
                    'affected_parameters': parameters
                })
            
            if any('Temperature' in p for p in parameters):
                temp_values = [a['value'] for a in critical_abnormalities if 'Temperature' in a['parameter']]
                if temp_values and temp_values[0] > 39:
                    alerts.append({
                        'alert_level': 'Critical',
                        'message': 'Severe Fever/Hyperthermia Detected',
                        'recommended_intervention': 'Assess for heat stroke. Implement cooling measures. Notify physician. Culture for infection. Consider central cooling device.',
                        'affected_parameters': parameters
                    })
                elif temp_values and temp_values[0] < 35:
                    alerts.append({
                        'alert_level': 'Critical',
                        'message': 'Severe Hypothermia Detected',
                        'recommended_intervention': 'Warm patient slowly. Notify physician. Assess for causes. Monitor for dysrhythmias (Osborn waves on ECG).',
                        'affected_parameters': parameters
                    })
            
            if any('Respiratory Rate' in p for p in parameters):
                alerts.append({
                    'alert_level': 'Critical',
                    'message': 'Critical Respiratory Rate Abnormality Detected',
                    'recommended_intervention': 'Notify physician immediately. Assess respiratory status. Check for airway obstruction. Prepare for mechanical ventilation if needed.',
                    'affected_parameters': parameters
                })
        
        # Generate Warning Alerts
        if warning_abnormalities and not critical_abnormalities:
            parameters = [a['parameter'] for a in warning_abnormalities]
            alert_message = f"Warning: Abnormal vital signs detected in {len(warning_abnormalities)} parameter(s)"
            alert_intervention = 'Monitor closely and reassess within 15 minutes. Notify nursing staff. Continue standard monitoring protocol.'
            
            alerts.append({
                'alert_level': 'Warning',
                'message': alert_message,
                'recommended_intervention': alert_intervention,
                'affected_parameters': parameters
            })
        
        return alerts
    
    def recommend_intervention(self, condition: str) -> str:
        """
        Map detected conditions to evidence-based interventions.
        
        Args:
            condition (str): Description of clinical condition
        
        Returns:
            str: Recommended intervention
        """
        condition_lower = condition.lower()
        
        # Oxygen-related conditions
        if 'hypoxia' in condition_lower or 'spo2' in condition_lower:
            return (
                'Supplemental Oxygen Protocol: '
                '1. Deliver oxygen to target SpO2 >94%. '
                '2. Use nasal cannula (1-6 L/min) or face mask as appropriate. '
                '3. If SpO2 remains <88%, prepare for non-invasive ventilation (CPAP/BiPAP). '
                '4. Notify respiratory therapy and physician. '
                '5. Reassess every 15 minutes initially.'
            )
        
        # Hypertension-related
        elif 'hypertension' in condition_lower or 'high blood pressure' in condition_lower:
            return (
                'Blood Pressure Management: '
                '1. Position patient at 30-45 degrees if not contraindicated. '
                '2. Verify reading accuracy (re-check in 5 minutes). '
                '3. Notify physician if SBP >160 or DBP >110. '
                '4. Consider antihypertensive medications as ordered. '
                '5. Monitor for headache, chest pain, or neurological changes.'
            )
        
        # Hypotension-related
        elif 'hypotension' in condition_lower or 'low blood pressure' in condition_lower:
            return (
                'Hypotension Management Protocol: '
                '1. Place patient in supine position. '
                '2. Initiate IV access (verify large bore). '
                '3. Increase IV fluid rate or initiate bolus as ordered. '
                '4. Notify physician if SBP <90 or MAP <65. '
                '5. Prepare vasopressor support if available. '
                '6. Assess for active bleeding or sepsis.'
            )
        
        # Tachycardia-related
        elif 'tachycardia' in condition_lower or 'high heart rate' in condition_lower:
            return (
                'Tachycardia Assessment: '
                '1. Obtain 12-lead ECG if HR >120 or irregular. '
                '2. Assess for pain, anxiety, fever, or dehydration. '
                '3. Establish IV access. '
                '4. Notify physician for rate >130 or if symptomatic. '
                '5. Consider beta-blocker or antiarrhythmic as ordered. '
                '6. Monitor for hemodynamic instability.'
            )
        
        # Bradycardia-related
        elif 'bradycardia' in condition_lower or 'low heart rate' in condition_lower:
            return (
                'Bradycardia Management: '
                '1. Obtain 12-lead ECG immediately. '
                '2. Establish IV access. '
                '3. Assess for symptoms (dizziness, hypotension). '
                '4. Notify physician if HR <50 or symptomatic. '
                '5. Have atropine and pacing pads available. '
                '6. Discontinue medications that slow heart rate (beta-blockers, CCBs) as ordered.'
            )
        
        # Fever-related
        elif 'fever' in condition_lower or 'high temperature' in condition_lower:
            return (
                'Fever Management Protocol: '
                '1. Obtain blood cultures x2 if fever >38.5°C. '
                '2. Administer antipyretics as ordered (acetaminophen or ibuprofen). '
                '3. Apply tepid water sponging if temp >39°C. '
                '4. Initiate broad-spectrum antibiotics if sepsis suspected. '
                '5. Notify physician and consider infectious disease consult. '
                '6. Monitor for delirium or seizures in high-risk patients.'
            )
        
        # Hypothermia-related
        elif 'hypothermia' in condition_lower or 'low temperature' in condition_lower:
            return (
                'Hypothermia Management: '
                '1. Passive rewarming for mild hypothermia (blankets, warm fluids). '
                '2. Active rewarming for severe hypothermia (heating blankets, warm IV fluids). '
                '3. Monitor ECG for Osborn waves. '
                '4. Avoid over-aggressive rewarming to prevent afterdrop. '
                '5. Notify physician and intensivist. '
                '6. Prepare for ECMO if core temp <30°C and unresponsive.'
            )
        
        # Default intervention
        else:
            return (
                'Standard Monitoring Protocol: '
                '1. Continuous cardiac monitoring. '
                '2. Vital sign reassessment every 15 minutes. '
                '3. Notify physician of any deterioration. '
                '4. Document findings in patient record. '
                '5. Ensure call bell within reach and provide reassurance to patient.'
            )
