"""
Flask application factory for the Intelligent Hospital Information System (I-HIS).
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()


def create_app(config_name='development'):
    """
    Application factory function.
    
    Args:
        config_name (str): Configuration environment ('development', 'testing', 'production')
    
    Returns:
        Flask: Configured Flask application instance
    """
    from config import config
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.patient import patient_bp
    from app.routes.receptionist_ai import receptionist_bp
    from app.routes.icu_ai import icu_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(receptionist_bp)
    app.register_blueprint(icu_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
