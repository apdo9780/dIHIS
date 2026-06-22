# I-HIS Quick Start Guide

## Getting Started in 5 Minutes

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd I-HIS

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (optional for development)
# Set FLASK_ENV=development for debug mode
```

### Step 3: Run the Application

```bash
python run.py
```

The application will start on **http://localhost:5000**

### Step 4: Access the System

- **Homepage**: http://localhost:5000/
- **Dashboard**: http://localhost:5000/dashboard
- **Patient Registration**: http://localhost:5000/patient/register
- **Receptionist AI**: http://localhost:5000/receptionist/interface

## Project Highlights

### ✅ Completed Week 1 Features

1. **Patient Management System**
   - Patient registration with comprehensive demographic data
   - Electronic Patient Records (EPR) with full medical history
   - Patient search and filtering
   - Edit patient information

2. **User Interface**
   - Responsive design with Bootstrap 5
   - Modern navigation with dropdown menus
   - Clean, intuitive layouts
   - Mobile-friendly interface

3. **Hospital Receptionist AI**
   - Patient triage assessment
   - Department routing recommendations
   - Appointment scheduling support
   - Guidance and basic counseling

4. **Database**
   - SQLAlchemy ORM models
   - Patient information storage
   - Appointment tracking
   - Automatic timestamps

5. **Forms & Validation**
   - Comprehensive patient registration form
   - Form validation with WTForms
   - Error messages and feedback
   - Data integrity checks

6. **API Endpoints**
   - RESTful patient data endpoints
   - AI triage endpoints
   - Appointment scheduling endpoints
   - JSON response support

## Key Routes

### Main Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Homepage |
| `/dashboard` | GET | Clinical dashboard |
| `/about` | GET | About page |

### Patient Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/patient/register` | GET, POST | Register new patient |
| `/patient/search` | GET, POST | Search patients |
| `/patient/view/<id>` | GET | View patient EPR |
| `/patient/edit/<id>` | GET, POST | Edit patient |
| `/patient/api/patient/<id>` | GET | Get patient JSON |
| `/patient/api/search?q=...` | GET | Search patients JSON |

### Receptionist AI Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/receptionist/interface` | GET | AI interface |
| `/receptionist/api/register-patient` | POST | Register via AI |
| `/receptionist/api/triage-patient` | POST | Triage assessment |
| `/receptionist/api/schedule-appointment` | POST | Schedule appointment |
| `/receptionist/api/get-guidance/<id>` | GET | Get AI guidance |

## Database

### Automatic Setup
- Database creates automatically on first run
- Located at: `instance/i_his.db`
- SQLite format (no external dependencies)

### Reset Database
```bash
# Delete existing database
rm instance/i_his.db

# Restart application
python run.py
```

## File Structure

```
I-HIS/
├── app/
│   ├── __init__.py           # App factory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── patient.py        # Patient model
│   │   └── appointment.py    # Appointment model
│   ├── forms/
│   │   ├── __init__.py
│   │   └── patient.py        # Registration forms
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py           # Main routes
│   │   ├── patient.py        # Patient routes
│   │   └── receptionist_ai.py # AI routes
│   ├── ai_agents/
│   │   ├── __init__.py
│   │   └── receptionist.py   # AI logic
│   ├── templates/
│   │   ├── base.html         # Base template
│   │   ├── index.html        # Homepage
│   │   ├── dashboard.html
│   │   ├── about.html
│   │   ├── 404.html
│   │   ├── 500.html
│   │   ├── patient/          # Patient templates
│   │   └── receptionist/     # AI templates
│   └── static/
│       ├── css/style.css
│       └── js/main.js
├── instance/                 # Database location
├── config.py                # Configuration
├── requirements.txt         # Dependencies
├── run.py                   # Entry point
├── README.md                # Full documentation
├── QUICK_START.md           # This file
└── .env.example             # Environment template
```

## Testing the Application

### Test Patient Registration
1. Navigate to `http://localhost:5000/patient/register`
2. Fill in the patient form with test data
3. Submit the form
4. A unique MRN will be generated
5. Patient record will be created and displayed

### Test Patient Search
1. Navigate to `http://localhost:5000/patient/search`
2. Search by MRN, first name, or last name
3. Click "View" to see the full patient record
4. Click "Edit" to modify patient information

### Test Receptionist AI
1. Navigate to `http://localhost:5000/receptionist/interface`
2. Fill in patient information
3. Enter chief complaint and symptoms
4. Click "Run Triage Assessment"
5. AI will provide department recommendation and guidance

## Configuration

### Development Mode
```python
# Automatic in development:
DEBUG = True
TESTING = False
```

### Production Mode
```python
# Set environment variable:
FLASK_ENV=production
```

### Database Configuration
```python
# Modify in config.py:
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/i_his.db'

# For PostgreSQL (future):
# SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/i_his'
```

### AI Configuration
```python
# Set in .env:
AI_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

## Common Issues & Solutions

### Issue: Port 5000 already in use
```bash
# Use a different port:
python -c "from app import create_app; app = create_app(); app.run(port=5001)"
```

### Issue: Database locked
```bash
# Delete database and restart:
rm instance/i_his.db
python run.py
```

### Issue: Module not found
```bash
# Reinstall requirements:
pip install -r requirements.txt --upgrade
```

### Issue: Template not found
```bash
# Make sure templates directory exists:
# app/templates/ directory with subdirectories
```

## Next Steps

1. **Test all features** in the application
2. **Customize** branding and settings
3. **Add users** and authentication (Week 2+)
4. **Integrate AI providers** (Gemini, OpenAI)
5. **Deploy** to production server
6. **Add more specialists** (upcoming weeks)

## Development Tips

### Debug Mode
```bash
export FLASK_ENV=development
python run.py
```

### Access Debug Console
- Application runs with debugger enabled
- Click "Debugger" in browser on error
- Interactive debugging available

### Shell Access
```bash
export FLASK_APP=run.py
flask shell
>>> from app import db
>>> from app.models import Patient
>>> Patient.query.all()
```

### Creating Test Data
```python
from app import create_app, db
from app.models import Patient
from datetime import date

app = create_app()
with app.app_context():
    patient = Patient(
        mrn='I-HIS-TEST001',
        first_name='John',
        last_name='Doe',
        date_of_birth=date(1990, 1, 1),
        gender='Male',
        phone='5551234567',
        address='123 Main St',
        city='Springfield',
        state='IL',
        postal_code='62701',
        country='USA',
        emergency_contact_name='Jane Doe',
        emergency_contact_phone='5559876543'
    )
    db.session.add(patient)
    db.session.commit()
    print(f"Patient created: {patient.full_name}")
```

## Support & Documentation

- **Full README**: See [README.md](README.md)
- **Configuration**: See [config.py](config.py)
- **AI Module**: See [app/ai_agents/receptionist.py](app/ai_agents/receptionist.py)

## Course Information

**Program**: Professional Master's in AI in Healthcare  
**Term**: 2  
**Week**: 1 (Foundation)  
**Project**: Intelligent Hospital Information System (I-HIS)

---

**Happy Coding! 🏥✨**
