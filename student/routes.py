from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from auth.routes import student_required
from models import Course, Enrollment, User
from extensions import db
import csv
from io import StringIO
from . import student_bp
from datetime import datetime

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    # Check for year progression eligibility first
    year_progression_message = None
    if current_user.is_student() and current_user.department_id and current_user.year_level:
        eligible, next_year, completed_count = current_user.check_year_progression_eligibility()
        if eligible and next_year:
            # Promote student to next year
            success, message = current_user.promote_to_next_year()
            if success:
                db.session.commit()
                year_progression_message = f"🎉 Congratulations! You have successfully completed all Year {current_user.year_level - 1} courses and have been promoted to Year {current_user.year_level}!"
                flash(year_progression_message, 'success')

    # Get enrolled courses with grades
    enrolled_courses = Enrollment.query.filter_by(student_id=current_user.id).all()

    show_department_course_sections = True
    # Get courses from student's department only, and automatically determine semester
    if not getattr(current_user, 'department', None) or current_user.department_id is None:
        department_courses = []
        show_department_course_sections = False
    else:
        # Get courses for student's current year level and department
        department_courses = Course.query.filter_by(
            department_id=current_user.department_id,
            year_required=current_user.year_level
        ).all()

        # Automatically determine which semester courses to show
        if year_progression_message:
            # If student was just promoted, show 1st semester courses of their new year level
            department_courses = [c for c in department_courses if c.semester == '1st']
        else:
            # Check if all 1st semester courses are graded
            if current_user.are_all_current_semester_courses_graded('1st'):
                # Show 2nd semester courses if all 1st semester courses are graded
                department_courses = [c for c in department_courses if c.semester == '2nd']
            else:
                # Show 1st semester courses if not all are graded yet
                department_courses = [c for c in department_courses if c.semester == '1st']
    eligible_courses = []
    ineligible_courses = []
    
    for course in department_courses:
        # Check if already enrolled
        existing_enrollment = Enrollment.query.filter_by(
            student_id=current_user.id,
            course_id=course.id
        ).first()
        
        if existing_enrollment:
            # Don't show courses that are already enrolled (no automatic retake)
            continue
            
        # Check eligibility for new enrollment
        is_eligible, message = course.is_eligible_for_student(current_user)
        if is_eligible:
            eligible_courses.append({
                'course': course,
                'message': message,
                'is_retake': False,
                'previous_grade': None
            })
        else:
            if course.year_required == current_user.year_level:
                ineligible_courses.append({
                    'course': course,
                    'reason': message
                })
    
    return render_template('student/dashboard.html',
                         enrolled_courses=enrolled_courses,
                         eligible_courses=eligible_courses,
                         ineligible_courses=ineligible_courses,
                         show_department_course_sections=show_department_course_sections,
                         year_progression_message=year_progression_message)

@student_bp.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
@student_required
def enroll_course(course_id):
    """Enroll in a specific course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if course is from student's department
    if course.department_id != current_user.department_id:
        flash('You can only enroll in courses from your department.', 'error')
        return redirect(url_for('student.dashboard'))
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        student_id=current_user.id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course.', 'error')
        return redirect(url_for('student.dashboard'))
    
    # Check eligibility
    is_eligible, message = course.is_eligible_for_student(current_user)
    if not is_eligible:
        flash(message, 'error')
        return redirect(url_for('student.dashboard'))
    
    # Create new enrollment
    enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    
    flash(f'Successfully enrolled in {course.name}', 'success')
    return redirect(url_for('student.dashboard'))

@student_bp.route('/bulk-enroll', methods=['POST'])
@login_required
@student_required
def bulk_enroll():
    """Bulk enroll in multiple courses"""
    course_ids = request.form.getlist('course_ids')
    
    if not course_ids:
        flash('No courses selected for enrollment.', 'error')
        return redirect(url_for('student.dashboard'))
    
    success_count = 0
    error_count = 0
    
    for course_id in course_ids:
        try:
            course = Course.query.get(course_id)
            if not course:
                error_count += 1
                continue
            
            # Check if course is from student's department
            if course.department_id != current_user.department_id:
                error_count += 1
                continue
            
            # Check if already enrolled
            existing_enrollment = Enrollment.query.filter_by(
                student_id=current_user.id,
                course_id=course_id
            ).first()
            
            if existing_enrollment:
                error_count += 1
                continue
            
            # Check eligibility
            is_eligible, message = course.is_eligible_for_student(current_user)
            if not is_eligible:
                error_count += 1
                continue
            
            # Create new enrollment
            enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
            db.session.add(enrollment)
            success_count += 1
            
        except Exception:
            error_count += 1
    
    try:
        db.session.commit()
        if success_count > 0:
            flash(f'Successfully enrolled in {success_count} course(s)', 'success')
        if error_count > 0:
            flash(f'Failed to enroll in {error_count} course(s)', 'error')
    except Exception:
        db.session.rollback()
        flash('An error occurred during enrollment.', 'error')
    
    return redirect(url_for('student.dashboard'))

@student_bp.route('/api/eligible')
@login_required
@student_required
def api_eligible_courses():
    """API endpoint to get eligible courses for the current student"""
    # Get courses from student's department and current year level, automatically determine semester
    department_courses = Course.query.filter_by(
        department_id=current_user.department_id,
        year_required=current_user.year_level
    ).all()

    # Automatically determine which semester courses to show
    if current_user.are_all_current_semester_courses_graded('1st'):
        # Show 2nd semester courses if all 1st semester courses are graded
        department_courses = [c for c in department_courses if c.semester == '2nd']
    else:
        # Show 1st semester courses if not all are graded yet
        department_courses = [c for c in department_courses if c.semester == '1st']

    eligible_courses = []
    
    for course in department_courses:
        # Check if already enrolled
        existing_enrollment = Enrollment.query.filter_by(
            student_id=current_user.id,
            course_id=course.id
        ).first()
        
        if existing_enrollment:
            # If it's a failed course, allow retake
            if existing_enrollment.can_retake():
                eligible_courses.append({
                    'id': course.id,
                    'code': course.code,
                    'name': course.name,
                    'year_required': course.year_required,
                    'department': course.department.name if course.department else None,
                    'message': 'Eligible for retake (previous grade: {})'.format(existing_enrollment.grade),
                    'is_retake': True,
                    'previous_grade': existing_enrollment.grade
                })
            continue
            
        # Check eligibility for new enrollment
        is_eligible, message = course.is_eligible_for_student(current_user)
        if is_eligible:
            eligible_courses.append({
                'id': course.id,
                'code': course.code,
                'name': course.name,
                'year_required': course.year_required,
                'department': course.department.name if course.department else None,
                'message': message,
                'is_retake': False,
                'previous_grade': None
            })
    
    return jsonify(eligible_courses)

@student_bp.route('/export/enrollments')
@login_required
@student_required
def export_enrollments():
    """Export student enrollments to CSV"""
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Course Code', 'Course Name', 'Department', 'Grade', 'Status', 'Enrollment Date'])
    
    for enrollment in enrollments:
        course = enrollment.course
        grade = enrollment.grade if enrollment.grade else 'Not Graded'
        status = enrollment.get_status()
        dept_name = course.department.name if course.department else 'N/A'
        writer.writerow([
            course.code,
            course.name,
            dept_name,
            grade,
            status,
            enrollment.enrolled_at.strftime('%Y-%m-%d')
        ])
    
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=enrollments.csv'
    }
