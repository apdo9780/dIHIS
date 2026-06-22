# I-HIS Architecture & Design Documentation

## System Overview

The Intelligent Hospital Information System (I-HIS) is a modular, scalable healthcare platform built with Flask. It integrates patient management, electronic records, and AI-powered clinical decision support.

## Architecture Pattern

### Three-Tier Architecture

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (Templates, Forms, Frontend JS)        │
└────────────────┬────────────────────────┘
                 │
┌────────────────┴────────────────────────┐
│         Application Layer               │
│  (Routes, Forms, Business Logic)        │
└────────────────┬────────────────────────┘
                 │
┌────────────────┴────────────────────────┐
│         Data Access Layer               │
│  (Models, ORM, Database)                │
└─────────────────────────────────────────┘
```

## Core Components

### 1. Application Factory (app/__init__.py)

```python
def create_app(config_name='development'):
    """
    Application factory pattern implementation
    - Initializes Flask app
    - Configures extensions (SQLAlchemy, WTForms)
    - Registers blueprints
    - Creates database tables
    """
```

**Benefits**:
- Separation of configuration and initialization
- Easy testing with different configurations
- Multiple app instances possible
- Clean dependency injection

### 2. Database Layer (app/models/)

#### Patient Model
```python
class Patient(db.Model):
    - Comprehensive patient information
    - Medical history tracking
    - Appointment relationships
    - Timestamps for audit trail
```

**Features**:
- Unique MRN (Medical Record Number)
- Medical history and allergies
- Emergency contact information
- Visit tracking
- Relationship to Appointments

#### Appointment Model
```python
class Appointment(db.Model):
    - Links to Patient via foreign key
    - Department and reason
    - Status tracking
    - Notes field for documentation
```

### 3. Forms Layer (app/forms/)

#### PatientRegistrationForm
- Comprehensive field validation
- Bootstrap styling integration
- Error message handling
- Email uniqueness checking

#### PatientSearchForm
- Simple search interface
- Flexible query matching

**Form Features**:
- CSRF protection via Flask-WTF
- Data validation with validators
- Custom error messages
- Bootstrap CSS classes
- Accessible form design

### 4. Routes Layer (app/routes/)

#### Main Routes (main.py)
- Homepage
- Dashboard
- About page
- Error handling (404, 500)

#### Patient Routes (patient.py)
- Patient registration (GET/POST)
- Patient search (GET/POST)
- View EPR (GET)
- Edit patient (GET/POST)
- API endpoints (JSON)

#### Receptionist AI Routes (receptionist_ai.py)
- AI interface (GET)
- Register patient via AI (POST)
- Triage assessment (POST)
- Appointment scheduling (POST)
- Guidance endpoints (GET)

### 5. AI Layer (app/ai_agents/)

#### ReceptionistAI Class
```python
class ReceptionistAI:
    - Department mapping logic
    - Triage assessment
    - Symptom analysis
    - Appointment guidance
    - Patient routing
```

**Key Methods**:
- `assess_triage()` - Determine priority level
- `recommend_department()` - Route to correct department
- `check_appointment_availability()` - Check scheduling
- `provide_guidance()` - Patient instructions
- `set_llm_provider()` - Configure AI backend (future)

**Design Philosophy**:
- Modular and extensible
- Ready for LLM integration (Gemini, OpenAI)
- Rule-based fallback system
- Easy to test and mock

### 6. Template Layer (app/templates/)

#### Base Template (base.html)
- Navigation bar
- Flash message handling
- Footer
- Static assets loading
- Block inheritance structure

#### Page Templates
- `index.html` - Homepage with features
- `dashboard.html` - Clinical dashboard
- `about.html` - Project information
- Error pages (404.html, 500.html)

#### Patient Templates
- `register.html` - Registration form
- `epr.html` - Electronic Patient Record view
- `search.html` - Patient search interface
- `edit.html` - Patient information editor

#### AI Templates
- `interface.html` - Receptionist AI interactive interface

### 7. Static Assets (app/static/)

#### CSS (style.css)
- Bootstrap customization
- Custom component styles
- Responsive design
- Print styles
- Smooth transitions

#### JavaScript (main.js)
- Utility functions
- API call wrapper
- Form validation
- Notification system
- Bootstrap initialization

## Configuration Management (config.py)

### Three Configuration Classes

```python
class Config:              # Base settings
class DevelopmentConfig:   # Dev overrides
class TestingConfig:       # Test overrides
class ProductionConfig:    # Production overrides
```

### Configuration Dictionary
```python
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

**Key Settings**:
- Database URI
- Secret key
- Debug mode
- Session timeout
- File upload limits
- AI provider configuration

## Data Flow

### Patient Registration Flow

```
User Input (Form)
       ↓
Form Validation (WTForms)
       ↓
Patient Model Creation
       ↓
Database Insert (SQLAlchemy)
       ↓
MRN Generation
       ↓
Redirect to EPR View
       ↓
Display Success Message
```

### Triage Assessment Flow

```
Patient Data Input
       ↓
Symptom Analysis
       ↓
ReceptionistAI.assess_triage()
       ↓
Department Recommendation
       ↓
Triage Level Determination
       ↓
Availability Check
       ↓
JSON Response to Frontend
       ↓
Display Results
```

## Database Schema

### Patients Table
```sql
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    mrn VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20) NOT NULL,
    email VARCHAR(120) UNIQUE,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    emergency_contact_name VARCHAR(100) NOT NULL,
    emergency_contact_phone VARCHAR(20) NOT NULL,
    medical_history TEXT,
    allergies TEXT,
    current_medications TEXT,
    chief_complaint VARCHAR(255),
    reason_for_visit TEXT,
    assigned_department VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
)
```

### Appointments Table
```sql
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL FOREIGN KEY,
    appointment_date DATETIME NOT NULL,
    department VARCHAR(100) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## API Design

### REST Principles
- Resource-based URLs
- Standard HTTP methods
- JSON request/response
- Appropriate status codes

### Patient API Endpoints
```
GET  /patient/api/patient/<id>         → Get patient data
GET  /patient/api/search?q=<query>     → Search patients
```

### AI API Endpoints
```
POST /receptionist/api/register-patient       → Register via AI
POST /receptionist/api/triage-patient         → Assess triage
POST /receptionist/api/schedule-appointment   → Schedule appointment
GET  /receptionist/api/get-guidance/<id>     → Get guidance
```

## Security Considerations

### Implemented
- ✅ CSRF protection (Flask-WTF)
- ✅ XSS prevention (Jinja2 auto-escaping)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Input validation (WTForms)
- ✅ HTTP-only cookies

### Future Implementation
- 🔄 Authentication & Authorization
- 🔄 Password hashing (werkzeug.security)
- 🔄 Role-based access control (RBAC)
- 🔄 API authentication (JWT/OAuth)
- 🔄 HTTPS enforcement
- 🔄 Rate limiting
- 🔄 Data encryption

## Modularity & Extensibility

### Adding New Routes
```python
# Create new blueprint
new_bp = Blueprint('feature', __name__, url_prefix='/feature')

@new_bp.route('/path', methods=['GET', 'POST'])
def handler():
    return render_template('template.html')

# Register in app/__init__.py
app.register_blueprint(new_bp)
```

### Adding New Models
```python
# Create in app/models/
class NewModel(db.Model):
    __tablename__ = 'new_models'
    # Define fields

# Import in app/models/__init__.py
```

### Adding New Forms
```python
# Create in app/forms/
class NewForm(FlaskForm):
    field = StringField(...)

# Import in app/forms/__init__.py
```

### Adding New AI Agents
```python
# Create in app/ai_agents/
class NewAgent:
    def __init__(self):
        pass
    
    def process(self, data):
        return result

# Import in app/ai_agents/__init__.py
```

## Testing Strategy

### Unit Tests
```python
# Test models
def test_patient_full_name():
    patient = Patient(first_name='John', last_name='Doe')
    assert patient.full_name == 'John Doe'

# Test AI logic
def test_triage_assessment():
    ai = ReceptionistAI()
    result = ai.assess_triage('chest pain')
    assert result['priority'] == 'urgent'
```

### Integration Tests
```python
# Test routes
def test_patient_registration():
    response = client.post('/patient/register', data={...})
    assert response.status_code == 302

# Test database
def test_patient_save():
    patient = Patient(...)
    db.session.add(patient)
    db.session.commit()
    assert Patient.query.count() == 1
```

## Performance Considerations

### Database Optimization
- Index on MRN for fast lookups
- Index on email for uniqueness checks
- Lazy loading for relationships
- Query optimization

### Caching Strategy (Future)
- Cache department availability
- Cache common searches
- Session-based patient data

### Scalability Path
1. **Phase 1** (Current): SQLite, single server
2. **Phase 2**: PostgreSQL, horizontal scaling
3. **Phase 3**: Microservices, API gateway
4. **Phase 4**: Cloud deployment (AWS/GCP/Azure)

## Deployment Architecture

### Development
```
Local Machine
    ↓
Flask dev server (port 5000)
    ↓
SQLite database
```

### Production
```
Load Balancer
    ↓
Gunicorn/uWSGI Servers
    ↓
PostgreSQL Database
    ↓
Object Storage (S3)
```

## Week 1 Implementation Summary

### Completed Features
✅ Patient registration system  
✅ Electronic patient records  
✅ Patient search and management  
✅ Receptionist AI module  
✅ Department routing  
✅ Appointment scheduling  
✅ Responsive UI  
✅ Database with relationships  

### Code Statistics
- **Total Files**: 30+
- **Lines of Python**: 1500+
- **Lines of HTML**: 1200+
- **Lines of CSS**: 300+
- **Routes**: 12+
- **Database Models**: 2
- **Templates**: 11+

## Future Architecture Plans

### Week 2-3: Additional AI Modules
```
ReceptionistAI → GeneralPractitionerAI
              → ICUSpecialistAI
              → RadiologistAI
```

### Week 4-5: Advanced Features
```
Dashboard enhancements
Real-time notifications
Medical imaging integration
Chatbot implementation
```

### Week 6-13: System Integration
```
Multi-agent orchestration
Complex clinical workflows
Treatment optimization
Reinforcement learning integration
```

## Lessons Learned & Best Practices

1. **App Factory Pattern**
   - Better testability
   - Configuration flexibility
   - Code organization

2. **Blueprints for Organization**
   - Modular route structure
   - Easy to scale
   - Clear separation of concerns

3. **Model Relationships**
   - Foreign keys for data integrity
   - Cascade delete for cleanup
   - Lazy loading for performance

4. **Form Validation**
   - Server-side validation critical
   - WTForms handles CSRF
   - Custom validators for business logic

5. **Template Inheritance**
   - DRY principle
   - Consistent styling
   - Easy maintenance

---

**Document Version**: 1.0  
**Last Updated**: Week 1  
**Status**: Active Development  
