from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from auth.routes import faculty_required
from models import Course, Enrollment, User, Department
from extensions import db
from . import faculty_bp

@faculty_bp.route('/dashboard')
@login_required
@faculty_required
def dashboard():
    """Faculty dashboard showing courses assigned to this faculty member"""
    if not current_user.department_id:
        flash('You are not assigned to any department.', 'error')
        return render_template('faculty/dashboard.html', courses=[])
    
    courses = Course.query.filter_by(faculty_id=current_user.id).all()
    return render_template('faculty/dashboard.html', courses=courses)

@faculty_bp.route('/courses')
@login_required
@faculty_required
def courses():
    """List all courses assigned to this faculty member"""
    if not current_user.department_id:
        flash('You are not assigned to any department.', 'error')
        return render_template('faculty/courses.html', courses=[])
    
    courses = Course.query.filter_by(faculty_id=current_user.id).all()
    return render_template('faculty/courses.html', courses=courses)

@faculty_bp.route('/course/<int:course_id>')
@login_required
@faculty_required
def course_detail(course_id):
    """View course details and enrolled students"""
    course = Course.query.get_or_404(course_id)
    
    # Check if faculty has access to this course
    if course.faculty_id != current_user.id:
        flash('You do not have access to this course.', 'error')
        return redirect(url_for('faculty.courses'))
    
    # Get enrolled students
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    
    return render_template('faculty/course_detail.html', 
                         course=course, 
                         enrollments=enrollments)

@faculty_bp.route('/course/<int:course_id>/grade/<int:enrollment_id>', methods=['POST'])
@login_required
@faculty_required
def assign_grade(course_id, enrollment_id):
    """Assign a grade to a student enrollment"""
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    # Check if faculty has access to this course
    if course.faculty_id != current_user.id:
        flash('You do not have access to this course.', 'error')
        return redirect(url_for('faculty.courses'))
    
    # Check if enrollment belongs to this course
    if enrollment.course_id != course_id:
        flash('Invalid enrollment.', 'error')
        return redirect(url_for('faculty.course_detail', course_id=course_id))
    
    try:
        grade = request.form.get('grade')
        
        # Handle clearing grade
        if grade is None or grade == '':
            enrollment.grade = None
        # Validate grade format
        elif grade == 'INC':
            enrollment.grade = 'INC'
        elif grade == 'RET':
            enrollment.grade = 'RET'
        else:
            try:
                grade_value = float(grade)
                # Check if it's a valid grade per new scale
                valid_grades = [1.0, 1.25, 1.50, 1.75, 2.0, 2.25, 2.50, 2.75, 3.0, 5.0]
                if grade_value not in valid_grades:
                    flash('Invalid grade value. Use 1.0, 1.25, 1.50, 1.75, 2.0, 2.25, 2.50, 2.75, 3.0, 3.25, 3.50, 3.75, 4.0, 5.0, or INC.', 'error')
                    return redirect(url_for('faculty.course_detail', course_id=course_id))
                enrollment.grade = str(grade_value)
            except ValueError:
                flash('Invalid grade value. Use 1.0, 1.25, 1.50, 1.75, 2.0, 2.25, 2.50, 2.75, 3.0, 3.25, 3.50, 3.75, 4.0, 5.0, or INC.', 'error')
                return redirect(url_for('faculty.course_detail', course_id=course_id))
        
        db.session.commit()
        
        student = User.query.get(enrollment.student_id)
        flash(f'Grade {grade} assigned to {student.get_full_name()} for {course.name}', 'success')
        
    except Exception as e:
        flash('An error occurred while assigning the grade.', 'error')
    
    return redirect(url_for('faculty.course_detail', course_id=course_id))

@faculty_bp.route('/course/<int:course_id>/bulk-grade', methods=['POST'])
@login_required
@faculty_required
def bulk_assign_grades(course_id):
    """Bulk assign grades to multiple students"""
    course = Course.query.get_or_404(course_id)
    
    # Check if faculty has access to this course
    if course.faculty_id != current_user.id:
        flash('You do not have access to this course.', 'error')
        return redirect(url_for('faculty.courses'))
    
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    success_count = 0
    error_count = 0
    
    for enrollment in enrollments:
        grade_key = f'grade_{enrollment.id}'
        if grade_key in request.form:
            try:
                grade = request.form[grade_key]
                
                # Validate grade format
                if grade is None or grade == '':
                    enrollment.grade = None
                    success_count += 1
                elif grade == 'INC':
                    enrollment.grade = 'INC'
                    success_count += 1
                elif grade == 'RET':
                    enrollment.grade = 'RET'
                    success_count += 1
                else:
                    try:
                        grade_value = float(grade)
                        # Check if it's a valid grade per new scale
                        valid_grades = [1.0, 1.25, 1.50, 1.75, 2.0, 2.25, 2.50, 2.75, 3.0, 5.0]
                        if grade_value in valid_grades:
                            enrollment.grade = str(grade_value)
                            success_count += 1
                        else:
                            error_count += 1
                    except ValueError:
                        error_count += 1
            except Exception:
                error_count += 1
    
    try:
        db.session.commit()
        if success_count > 0:
            flash(f'Successfully assigned grades to {success_count} student(s)', 'success')
        if error_count > 0:
            flash(f'Failed to assign grades to {error_count} student(s)', 'error')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred during bulk grade assignment.', 'error')
    
    return redirect(url_for('faculty.course_detail', course_id=course_id))

@faculty_bp.route('/course/<int:course_id>/re-enroll/<int:enrollment_id>', methods=['POST'])
@login_required
@faculty_required
def re_enroll_student(course_id, enrollment_id):
    """Re-enroll a failed student in the course"""
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    # Check if faculty has access to this course
    if course.faculty_id != current_user.id:
        flash('You do not have access to this course.', 'error')
        return redirect(url_for('faculty.courses'))
    
    # Check if enrollment belongs to this course
    if enrollment.course_id != course_id:
        flash('Invalid enrollment.', 'error')
        return redirect(url_for('faculty.course_detail', course_id=course_id))
    
    # Check if student can be re-enrolled (failed or incomplete)
    if not enrollment.can_retake():
        flash('Student cannot be re-enrolled. Only failed or incomplete students can be re-enrolled.', 'error')
        return redirect(url_for('faculty.course_detail', course_id=course_id))
    
    try:
        # Mark as retaking and reset enrollment date
        enrollment.grade = 'RET'
        from datetime import datetime
        enrollment.enrolled_at = datetime.utcnow()

        db.session.commit()

        # On success, return to detail page which now shows status Retaking,
        # disables grade input, and hides re-enroll action (per template logic)
        student = User.query.get(enrollment.student_id)
        flash(f'{student.get_full_name()} has been re-enrolled in {course.name}', 'success')

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while re-enrolling the student.', 'error')

    return redirect(url_for('faculty.course_detail', course_id=course_id))
