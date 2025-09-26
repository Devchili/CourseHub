from flask import render_template, redirect, url_for
from flask_login import current_user
from . import main_bp

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_faculty():
            return redirect(url_for('faculty.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    return render_template('main/index.html')
