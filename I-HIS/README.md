# Intelligent Hospital Information System (I-HIS)

A comprehensive AI-powered healthcare management platform built with Flask.

## Features

- ✅ Patient Registration & Management
- ✅ Electronic Patient Records (EPR)
- ✅ Hospital Receptionist AI
- ✅ Patient Triage & Routing
- ✅ Appointment Scheduling
- ✅ Multi-Department Support
- 🔄 Modular Architecture (Ready for future AI specialists)

## Project Structure

```
I-HIS/
├── app/                      # Main application package
│   ├── __init__.py          # App factory
│   ├── models/              # Database models
│   │   ├── patient.py       # Patient model
│   │   └── appointment.py   # Appointment model
│   ├── forms/               # Flask-WTF forms
│   │   └── patient.py       # Patient registration forms
│   ├── routes/              # Application routes
│   │   ├── main.py          # Main routes
│   │   ├── patient.py       # Patient management routes
│   │   └── receptionist_ai.py # AI receptionist routes
│   ├── ai_agents/           # AI modules
│   │   └── receptionist.py  # Receptionist AI logic
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html        # Base template
│   │   ├── index.html       # Homepage
│   │   ├── patient/         # Patient templates
│   │   └── receptionist/    # AI templates
│   └── static/              # Static files
│       ├── css/
│       └── js/
├── instance/                # Instance folder (database, config)
├── config.py               # Configuration
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── .env.example            # Environment variables template
└── README.md              # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Instructions

1. **Clone or navigate to the project directory**
   ```bash
   cd I-HIS
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Initialize database**
   ```bash
   python run.py
   # The database will be created on first run
   ```

## Usage

### Running the Application

```bash
python run.py
```

The application will start on `http://localhost:5000`

### Application Routes

- **Homepage**: `/` - Main landing page
- **Dashboard**: `/dashboard` - Clinical dashboard
- **Patient Registration**: `/patient/register` - Register new patient
- **Patient Search**: `/patient/search` - Search existing patients
- **Patient EPR**: `/patient/view/<id>` - View patient record
- **Edit Patient**: `/patient/edit/<id>` - Modify patient information
- **Receptionist AI**: `/receptionist/interface` - AI interface
- **About**: `/about` - Project information

### API Endpoints

#### Patient Management
- `GET /patient/api/patient/<id>` - Get patient data (JSON)
- `GET /patient/api/search?q=query` - Search patients (JSON)

#### Receptionist AI
- `POST /receptionist/api/register-patient` - AI patient registration
- `POST /receptionist/api/triage-patient` - AI triage assessment
- `POST /receptionist/api/schedule-appointment` - Schedule appointment
- `GET /receptionist/api/get-guidance/<patient_id>` - Get AI guidance

## Week 1 Deliverables

✅ **Functioning Flask-based HIS prototype**
✅ **Patient Registration Module**
✅ **Electronic Patient Record (EPR) Module**
✅ **Homepage and Navigation System**
✅ **Hospital Receptionist AI Integration**
✅ **Database Schema and Models**
✅ **RESTful API Endpoints**
✅ **Responsive UI (Bootstrap 5)**

## Technology Stack

### Backend
- **Framework**: Flask 2.3.3
- **ORM**: SQLAlchemy 2.0.21
- **Database**: SQLite
- **Forms**: Flask-WTF 1.1.1
- **API Integration**: Ready for Gemini & OpenAI

### Frontend
- **Templates**: Jinja2
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Bootstrap Icons
- **JavaScript**: Vanilla JS + Bootstrap JS

## AI Integration

The Hospital Receptionist AI module is designed to be modular and extensible:

```python
from app.ai_agents import ReceptionistAI

receptionist = ReceptionistAI()

# Set LLM provider (future feature)
receptionist.set_llm_provider('gemini', api_key='your-key')

# Use AI functions
department = receptionist.recommend_department(complaint)
triage = receptionist.assess_triage(complaint, symptoms)
```

## Database Schema

### Patients Table
- `id`: Primary key
- `mrn`: Medical Record Number (unique)
- `first_name`, `last_name`: Patient name
- `date_of_birth`: DOB
- `gender`: Gender
- `email`, `phone`: Contact info
- `address`, `city`, `state`, `postal_code`, `country`: Address
- `emergency_contact_name`, `emergency_contact_phone`
- `medical_history`, `allergies`, `current_medications`: Medical info
- `chief_complaint`, `reason_for_visit`: Visit info
- `assigned_department`: Department routing
- `created_at`, `updated_at`: Timestamps
- `status`: Patient status

### Appointments Table
- `id`: Primary key
- `patient_id`: Foreign key to Patients
- `appointment_date`: Scheduled date/time
- `department`: Department
- `reason`: Appointment reason
- `status`: Appointment status
- `notes`: Additional notes
- `created_at`: Timestamp

## Configuration

Edit `config.py` to customize:

```python
# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/i_his.db'

# AI Provider
AI_PROVIDER = 'gemini'
GEMINI_API_KEY = 'your-key'

# Session settings
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

# File upload
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

## Future Enhancements (Week 2-13)

- [ ] Disease Prediction Module (General Practitioner AI)
- [ ] Clinical Decision Support System (ICU Specialist AI)
- [ ] Medical Imaging Module (Radiologist AI)
- [ ] Healthcare Chatbot (Patient Education AI)
- [ ] Drug Interaction Checker (Pharmacist AI)
- [ ] Mental Health Assessment (Psychiatrist AI)
- [ ] Clinical Reasoning Engine
- [ ] Emergency Medicine AI (BFS Algorithm)
- [ ] Oncology Specialist (DFS Algorithm)
- [ ] Treatment Planning AI
- [ ] Multi-Agent Collaboration
- [ ] Final System Integration

## Security Considerations

- ✅ CSRF Protection (Flask-WTF)
- ✅ Password hashing (ready for implementation)
- ✅ SQL Injection prevention (SQLAlchemy)
- ✅ XSS Protection (Jinja2 auto-escaping)
- 🔄 HTTPS (configure in production)
- 🔄 API Authentication (future)
- 🔄 Role-based Access Control (future)

## Testing

```bash
# Run tests (to be implemented)
python -m pytest

# Run specific test file
python -m pytest tests/test_patient.py

# Run with coverage
pytest --cov=app
```

## Contributing

For development:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit pull request

## License

This project is part of the Professional Master's in AI in Healthcare program.

## Support & Documentation

For more information about the project structure and AI integration:
- See [Architecture Documentation](#)
- Check [API Documentation](#)
- Review [AI Agents Guide](#)

## Contact

Project Team - Professional Master's in AI in Healthcare
