# ICU CDSS Testing Guide - Quick Start

## Access the Dashboard

1. **Start the application**:
   ```bash
   cd I-HIS
   .\venv\Scripts\Activate.ps1
   python run.py
   ```

2. **Open browser**:
   ```
   http://localhost:5000/icu/dashboard
   ```

You should see the ICU Monitoring Dashboard with 4 summary cards and empty alert sections.

---

## Test Scenario 1: Record Normal Vitals

**Goal**: Verify the system accepts vital data and shows normal status.

**Using Python**:
```python
import requests
import json

# Assume Patient ID 1 exists from Week 1
response = requests.post(
    'http://localhost:5000/icu/api/vitals',
    json={
        'patient_id': 1,
        'heart_rate': 75,
        'blood_pressure_systolic': 120,
        'blood_pressure_diastolic': 80,
        'oxygen_saturation': 98.5,
        'temperature': 37.0,
        'respiratory_rate': 16
    }
)

print(json.dumps(response.json(), indent=2))
```

**Using curl** (PowerShell):
```powershell
$body = @{
    patient_id = 1
    heart_rate = 75
    blood_pressure_systolic = 120
    blood_pressure_diastolic = 80
    oxygen_saturation = 98.5
    temperature = 37.0
    respiratory_rate = 16
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/icu/api/vitals" `
    -Method Post `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body
```

**Expected Result**:
```json
{
    "success": true,
    "vital_sign_id": 1,
    "evaluation": {
        "is_normal": true,
        "overall_severity": "Normal",
        "abnormalities": []
    },
    "alerts_generated": [],
    "alert_count": 0,
    "message": "Vital signs recorded. All parameters normal."
}
```

✅ **Check**: Refresh dashboard - still no alerts (expected)

---

## Test Scenario 2: Trigger Warning Alert

**Goal**: Generate a warning-level alert from borderline vitals.

```python
response = requests.post(
    'http://localhost:5000/icu/api/vitals',
    json={
        'patient_id': 1,
        'heart_rate': 105,  # High normal -> Warning
        'blood_pressure_systolic': 145,  # Elevated
        'blood_pressure_diastolic': 92,  # Elevated
        'oxygen_saturation': 93.0,  # Slightly low
        'temperature': 37.0,
        'respiratory_rate': 18
    }
)
```

**Expected Result**:
```json
{
    "success": true,
    "alerts_generated": [
        {
            "alert_level": "Warning",
            "message": "Warning: Abnormal vital signs detected in 3 parameter(s)",
            "recommended_intervention": "Monitor closely and reassess within 15 minutes...",
            "affected_parameters": ["Heart Rate", "Systolic Blood Pressure", "Oxygen Saturation"]
        }
    ],
    "alert_count": 1
}
```

✅ **Check**: 
- Refresh dashboard
- Yellow alert should appear in "Warning Alerts" section
- Summary shows "1" in Total Alerts card

---

## Test Scenario 3: Trigger Critical Alert - Hypoxemia

**Goal**: Generate critical alert for life-threatening low oxygen.

```python
response = requests.post(
    'http://localhost:5000/icu/api/vitals',
    json={
        'patient_id': 1,
        'heart_rate': 125,  # Critical: Tachycardia
        'blood_pressure_systolic': 92,
        'blood_pressure_diastolic': 60,
        'oxygen_saturation': 82.0,  # CRITICAL: <85% SpO2
        'temperature': 37.0,
        'respiratory_rate': 28  # Critical: Tachypnea
    }
)
```

**Expected Result**:
```json
{
    "alerts_generated": [
        {
            "alert_level": "Critical",
            "message": "Severe Hypoxemia Detected - SpO2 critically low",
            "recommended_intervention": "EMERGENCY - Initiate oxygen therapy immediately..."
        },
        {
            "alert_level": "Critical",
            "message": "Severe Tachycardia Detected - Heart rate critically high",
            "recommended_intervention": "Immediate evaluation required. Notify physician..."
        },
        {
            "alert_level": "Critical",
            "message": "Critical Respiratory Rate Abnormality Detected",
            "recommended_intervention": "Notify physician immediately. Assess respiratory status..."
        }
    ],
    "alert_count": 3
}
```

✅ **Check**:
- Refresh dashboard
- 3 Red alerts appear in "Critical Clinical Alerts"
- Summary shows Critical Alerts: 3, Total Alerts: 4
- Each alert shows recommended intervention

---

## Test Scenario 4: Trigger Critical Alert - Sepsis Pattern

**Goal**: Generate critical alerts simulating sepsis (low BP, high temp, tachycardia).

```python
response = requests.post(
    'http://localhost:5000/icu/api/vitals',
    json={
        'patient_id': 1,
        'heart_rate': 135,  # Critical: Tachycardia
        'blood_pressure_systolic': 85,  # Critical: Hypotension
        'blood_pressure_diastolic': 50,
        'oxygen_saturation': 91.0,
        'temperature': 39.8,  # High fever
        'respiratory_rate': 26  # Critical: Tachypnea
    }
)
```

**Expected Multiple Critical Alerts**:
1. Severe Tachycardia
2. Severe Hypotension (Shock Risk!)
3. Critical Respiratory Rate
4. High Temperature/Fever

---

## Test Scenario 5: Test API - Get Alerts

**Goal**: Verify alert retrieval and filtering.

**Get All Unacknowledged Alerts**:
```python
response = requests.get(
    'http://localhost:5000/icu/api/alerts?acknowledged=false'
)
print(json.dumps(response.json(), indent=2))
```

**Get Only Critical Alerts**:
```python
response = requests.get(
    'http://localhost:5000/icu/api/alerts?acknowledged=false&alert_level=Critical'
)
```

**Get Specific Patient Alerts**:
```python
response = requests.get(
    'http://localhost:5000/icu/api/alerts?acknowledged=false&patient_id=1'
)
```

---

## Test Scenario 6: Acknowledge an Alert

**Goal**: Test alert acknowledgment workflow.

1. **Get an alert ID** from the previous scenario (e.g., alert_id = 5)

2. **Acknowledge it**:
   ```python
   response = requests.put(
       'http://localhost:5000/icu/api/alerts/5/acknowledge',
       json={
           'acknowledged_by': 'Dr. Smith'
       }
   )
   
   print(response.json())
   ```

3. **Expected Result**:
   ```json
   {
       "success": true,
       "alert": {
           "id": 5,
           "is_acknowledged": true,
           "acknowledged_at": "2024-01-15T14:45:00",
           "acknowledged_by": "Dr. Smith"
       },
       "message": "Alert 5 acknowledged"
   }
   ```

✅ **Check**: 
- In dashboard UI, click "Acknowledge Alert" button
- Alert should fade and disappear
- Critical/Total counts should decrease

---

## Test Scenario 7: Patient Vital History

**Goal**: Test retrieving historical vital signs.

**Get last 24 hours of vitals for patient 1**:
```python
response = requests.get(
    'http://localhost:5000/icu/api/vitals/1?hours=24&limit=100'
)

print(json.dumps(response.json(), indent=2))
```

**Expected Result**:
```json
{
    "success": true,
    "patient_id": 1,
    "patient_name": "John Doe",
    "mrn": "I-HIS-000001",
    "count": 4,
    "vitals": [
        {
            "id": 1,
            "heart_rate": 75,
            "blood_pressure_systolic": 120,
            ...
            "recorded_at": "2024-01-15T14:30:00"
        }
    ]
}
```

---

## Test Scenario 8: Real-time Dashboard Data

**Goal**: Test the data endpoint used by the dashboard polling.

```python
response = requests.get('http://localhost:5000/icu/api/dashboard-data')

print(json.dumps(response.json(), indent=2))
```

**Expected Result**:
```json
{
    "success": true,
    "timestamp": "2024-01-15T14:45:00",
    "summary": {
        "total_alerts": 3,
        "critical_alerts": 3,
        "warning_alerts": 0,
        "patients_monitored": 1,
        "recent_vitals_count": 4
    },
    "critical_alerts": [...],
    "warning_alerts": [...],
    "recent_patients": [...]
}
```

---

## Complete Test Script (Python)

```python
import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000'

def test_cdss():
    print("=" * 70)
    print("ICU CDSS Testing - Complete Workflow")
    print("=" * 70)
    
    # Test 1: Normal vitals
    print("\n[1] Recording normal vital signs...")
    response = requests.post(f'{BASE_URL}/icu/api/vitals', json={
        'patient_id': 1,
        'heart_rate': 75,
        'blood_pressure_systolic': 120,
        'blood_pressure_diastolic': 80,
        'oxygen_saturation': 98.5,
        'temperature': 37.0,
        'respiratory_rate': 16
    })
    assert response.status_code == 201
    data = response.json()
    assert data['evaluation']['is_normal'] == True
    assert data['alert_count'] == 0
    print("✅ PASS: Normal vitals recorded")
    
    # Test 2: Warning vitals
    print("\n[2] Recording warning-level vitals...")
    response = requests.post(f'{BASE_URL}/icu/api/vitals', json={
        'patient_id': 1,
        'heart_rate': 105,
        'blood_pressure_systolic': 145,
        'blood_pressure_diastolic': 92,
        'oxygen_saturation': 93.0,
        'temperature': 37.0,
        'respiratory_rate': 18
    })
    assert response.status_code == 201
    data = response.json()
    assert data['evaluation']['overall_severity'] == 'Warning'
    print(f"✅ PASS: Warning alert generated - {data['alerts_generated'][0]['message']}")
    
    # Test 3: Critical vitals
    print("\n[3] Recording critical hypoxemia vitals...")
    response = requests.post(f'{BASE_URL}/icu/api/vitals', json={
        'patient_id': 1,
        'heart_rate': 125,
        'blood_pressure_systolic': 92,
        'blood_pressure_diastolic': 60,
        'oxygen_saturation': 82.0,
        'temperature': 37.0,
        'respiratory_rate': 28
    })
    assert response.status_code == 201
    data = response.json()
    assert data['evaluation']['overall_severity'] == 'Critical'
    assert data['alert_count'] >= 1
    print(f"✅ PASS: {data['alert_count']} critical alerts generated")
    
    # Test 4: Get alerts
    print("\n[4] Retrieving alerts...")
    response = requests.get(f'{BASE_URL}/icu/api/alerts?acknowledged=false')
    assert response.status_code == 200
    data = response.json()
    alert_count = data['count']
    print(f"✅ PASS: Retrieved {alert_count} alerts")
    
    # Test 5: Get dashboard data
    print("\n[5] Fetching dashboard data...")
    response = requests.get(f'{BASE_URL}/icu/api/dashboard-data')
    assert response.status_code == 200
    data = response.json()
    print(f"✅ PASS: Dashboard data retrieved")
    print(f"   - Critical alerts: {data['summary']['critical_alerts']}")
    print(f"   - Total alerts: {data['summary']['total_alerts']}")
    print(f"   - Patients monitored: {data['summary']['patients_monitored']}")
    
    # Test 6: Get patient vitals
    print("\n[6] Retrieving patient vital history...")
    response = requests.get(f'{BASE_URL}/icu/api/vitals/1?hours=24')
    assert response.status_code == 200
    data = response.json()
    print(f"✅ PASS: Retrieved {data['count']} vital records for patient {data['mrn']}")
    
    # Test 7: Acknowledge alert
    print("\n[7] Testing alert acknowledgment...")
    response = requests.get(f'{BASE_URL}/icu/api/alerts?acknowledged=false&limit=1')
    alerts = response.json()['alerts']
    if alerts:
        alert_id = alerts[0]['id']
        response = requests.put(
            f'{BASE_URL}/icu/api/alerts/{alert_id}/acknowledge',
            json={'acknowledged_by': 'Test Clinician'}
        )
        assert response.status_code == 200
        print(f"✅ PASS: Alert {alert_id} acknowledged")
    else:
        print("⚠️  SKIP: No alerts to acknowledge")
    
    print("\n" + "=" * 70)
    print("All Tests Passed! ✅")
    print("=" * 70)

if __name__ == '__main__':
    test_cdss()
```

**Run the test**:
```bash
python test_cdss.py
```

---

## Dashboard Visual Inspection Checklist

After running the test scenarios, verify on the dashboard:

- [ ] Summary cards display current counts
- [ ] Critical alerts appear in red section with interventions
- [ ] Warning alerts appear in yellow section
- [ ] Patient cards show all 6 vital parameters
- [ ] SpO2 color changes based on value (green/yellow/red)
- [ ] Temperature shows correct unit (°C)
- [ ] Blood pressure formats correctly (Systolic/Diastolic)
- [ ] All patient links work
- [ ] Acknowledge buttons functional
- [ ] Dashboard updates every 5 seconds (check timestamp)
- [ ] No JavaScript errors in console (F12)

---

## Troubleshooting

### "Patient not found" error
- First register a patient at `/patient/register`
- Note the patient ID
- Use that ID in API calls

### Alerts not showing
- Check the Python test output - verify alert_count > 0
- Refresh browser (hard refresh: Ctrl+F5)
- Check browser console for errors (F12)
- Verify vital thresholds are being crossed

### Dashboard not updating
- Check if `/icu/api/dashboard-data` returns data
- Open browser console - look for fetch errors
- Verify Flask server is running
- Try manual refresh

### 404 Errors
- Verify application is running on port 5000
- Check routes: `/icu/dashboard`, `/icu/api/vitals`, etc.
- Verify blueprints registered in `app/__init__.py`

---

## Success Indicators

✅ You've successfully implemented CDSS when:

1. Dashboard loads without errors
2. Vital signs can be recorded via API
3. Critical conditions trigger alerts
4. Alerts appear on dashboard within 5 seconds
5. Acknowledging alerts updates the display
6. All API endpoints return valid JSON
7. No JavaScript errors in browser console
8. Patient vital history retrieves correctly

---

**Ready to test?** Start with Test Scenario 1 and work through sequentially!

