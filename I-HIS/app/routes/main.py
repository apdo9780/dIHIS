"""
Main routes for the I-HIS application (Homepage, Navigation).
"""
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage route."""
    return render_template('index.html')


@main_bp.route('/about')
def about():
    """About page route."""
    return render_template('about.html')


@main_bp.route('/dashboard')
def dashboard():
    """Dashboard route."""
    return render_template('dashboard.html')


@main_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('500.html'), 500
