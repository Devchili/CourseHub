from flask import Flask, render_template
from extensions import db, login_manager
from models import User
from auth import auth_bp
from student import student_bp
from faculty import faculty_bp
from admin import admin_bp
from main import main_bp
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///course_checker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    
    # Error handlers
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Safe migration: remove Department.semester column if it exists
        from sqlalchemy import inspect
        from models import Department
        inspector = inspect(db.engine)
        cols = [c['name'] for c in inspector.get_columns('department')]
        if 'semester' in cols:
            # Drop the semester column since we're now using automatic semester progression
            db.session.execute(db.text("ALTER TABLE department DROP COLUMN semester"))
            db.session.commit()
        db.create_all()
    app.run(debug=True)

