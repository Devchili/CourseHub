from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from auth.routes import admin_required
from models import User, Department, Course, Enrollment
from extensions import db
from sqlalchemy.exc import IntegrityError
import csv
from io import StringIO
from . import admin_bp

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with overview statistics"""
    total_students = User.query.filter_by(role='student').count()
    total_faculty = User.query.filter_by(role='faculty').count()
    total_courses = Course.query.count()
    total_departments = Department.query.count()
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         total_faculty=total_faculty,
                         total_courses=total_courses,
                         total_departments=total_departments)

# Department Management
@admin_bp.route('/departments')
@login_required
@admin_required
def departments():
    """List all departments"""
    departments = Department.query.all()
    return render_template('admin/crud/departments.html', departments=departments)

@admin_bp.route('/departments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_department():
    """Add a new department"""
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            department = Department(name=name)
            db.session.add(department)
            db.session.commit()
            flash(f'Department "{name}" added successfully.', 'success')
            return redirect(url_for('admin.departments'))
        else:
            flash('Department name is required.', 'error')
    
    return render_template('admin/crud/add_department.html')

@admin_bp.route('/departments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_department(id):
    """Edit a department"""
    department = Department.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            department.name = name
            db.session.commit()
            flash(f'Department "{name}" updated successfully.', 'success')
            return redirect(url_for('admin.departments'))
        else:
            flash('Department name is required.', 'error')
    
    return render_template('admin/crud/edit_department.html', department=department)

@admin_bp.route('/departments/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_department(id):
    """Delete a department"""
    department = Department.query.get_or_404(id)
    
    # Check if department has courses or users
    if department.courses.count() > 0:
        flash('Cannot delete department with existing courses.', 'error')
        return redirect(url_for('admin.departments'))
    
    if department.users.count() > 0:
        flash('Cannot delete department with existing users.', 'error')
        return redirect(url_for('admin.departments'))
    
    db.session.delete(department)
    db.session.commit()
    flash(f'Department "{department.name}" deleted successfully.', 'success')
    return redirect(url_for('admin.departments'))

# Course Management
@admin_bp.route('/courses')
@login_required
@admin_required
def courses():
    """List all courses"""
    courses = Course.query.all()
    return render_template('admin/crud/courses.html', courses=courses)

@admin_bp.route('/courses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    """Add a new course"""
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        year_required = request.form.get('year_required')
        semester = request.form.get('semester')
        is_ready = request.form.get('is_ready') == 'on'
        department_id = request.form.get('department_id')
        # Handle multiple prerequisites (optional, max 2)
        prereq_ids = request.form.getlist('prerequisite_ids')
        prereq_ids = [int(pid) for pid in prereq_ids if pid]
        if len(prereq_ids) > 2:
            flash('You can select up to two prerequisite courses only.', 'error')
            return redirect(url_for('admin.add_course'))
        faculty_id = request.form.get('faculty_id') or None
        
        if code and name and year_required and semester and department_id:
            try:
                # Prevent duplicate course codes
                existing = Course.query.filter_by(code=code).first()
                if existing:
                    flash('Course code already exists. Please use a unique code.', 'error')
                    return redirect(url_for('admin.add_course'))

                course = Course(
                    code=code,
                    name=name,
                    year_required=int(year_required),
                    semester=semester,
                    is_ready=is_ready,
                    department_id=int(department_id),
                    faculty_id=int(faculty_id) if faculty_id else None
                )
                db.session.add(course)
                db.session.flush()
                # Assign multiple prerequisites if provided
                if prereq_ids:
                    # Limit to max 2
                    prereq_ids = prereq_ids[:2]
                    course.prerequisites = Course.query.filter(Course.id.in_(prereq_ids)).all()
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    flash('Course code must be unique. A course with this code already exists.', 'error')
                    return redirect(url_for('admin.add_course'))
                flash(f'Course "{name}" added successfully.', 'success')
                return redirect(url_for('admin.courses'))
            except ValueError:
                flash('Invalid input values.', 'error')
        else:
            flash('All required fields must be filled.', 'error')
    
    departments = Department.query.all()
    courses = Course.query.all()  # for prerequisites
    faculty = User.query.filter_by(role='faculty').all()
    
    return render_template('admin/crud/add_course.html',
                         departments=departments,
                         courses=courses,
                         faculty=faculty)

@admin_bp.route('/courses/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(id):
    """Edit a course"""
    course = Course.query.get_or_404(id)
    
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        year_required = request.form.get('year_required')
        semester = request.form.get('semester')
        is_ready = request.form.get('is_ready') == 'on'
        department_id = request.form.get('department_id')
        prereq_ids = request.form.getlist('prerequisite_ids')
        prereq_ids = [int(pid) for pid in prereq_ids if pid]
        faculty_id = request.form.get('faculty_id') or None

        print("--- DEBUG: Edit Course Form Data ---")
        print(f"code: {code}")
        print(f"name: {name}")
        print(f"year_required: {year_required}")
        print(f"semester: {semester}")
        print(f"is_ready: {is_ready}")
        print(f"department_id: {department_id}")
        print(f"prereq_ids: {prereq_ids}")
        print(f"faculty_id: {faculty_id}")

        missing_fields = []
        if not code:
            missing_fields.append('code')
        if not name:
            missing_fields.append('name')
        if not year_required:
            missing_fields.append('year_required')
        if not semester:
            missing_fields.append('semester')
        if not department_id:
            missing_fields.append('department_id')
        if missing_fields:
            print(f"Missing fields: {missing_fields}")
            flash(f"All required fields must be filled. Missing: {', '.join(missing_fields)}", 'error')
            return redirect(url_for('admin.edit_course', id=id))

        if len(prereq_ids) > 2:
            flash('You can select up to two prerequisite courses only.', 'error')
            return redirect(url_for('admin.edit_course', id=id))

        try:
            course.code = code
            course.name = name
            course.year_required = int(year_required)
            course.semester = semester
            course.is_ready = is_ready
            course.department_id = int(department_id)
            course.prerequisites = []
            if prereq_ids:
                prereq_ids = prereq_ids[:2]
                course.prerequisites = Course.query.filter(Course.id.in_(prereq_ids)).all()
            course.faculty_id = int(faculty_id) if faculty_id else None
            db.session.commit()
            flash(f'Course "{name}" updated successfully.', 'success')
            return redirect(url_for('admin.courses'))
        except ValueError:
            print("ValueError occurred during course update.")
            flash('Invalid input values.', 'error')
    
    departments = Department.query.all()
    courses = Course.query.filter(Course.id != id).all()  # exclude current course from prerequisites
    faculty = User.query.filter_by(role='faculty').all()
    
    return render_template('admin/crud/edit_course.html',
                         course=course,
                         departments=departments,
                         courses=courses,
                         faculty=faculty)

@admin_bp.route('/courses/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_course(id):
    """Delete a course"""
    course = Course.query.get_or_404(id)
    
    # Unenroll students and clear associations before deletion
    try:
        # Delete enrollments for this course (unenroll students)
        Enrollment.query.filter_by(course_id=course.id).delete(synchronize_session=False)

        # Clear this course as a prerequisite from other courses
        dependents = course.dependent_courses.all() if hasattr(course, 'dependent_courses') else []
        for dependent in dependents:
            dependent.prerequisites.remove(course)

        # Clear legacy single prerequisite references
        Course.query.filter_by(prerequisite_id=course.id).update({Course.prerequisite_id: None})

        db.session.delete(course)
        db.session.commit()
        flash(f'Course "{course.name}" deleted successfully and students unenrolled.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to delete course: {str(e)}', 'error')
    return redirect(url_for('admin.courses'))

# User Management
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """List all users with search functionality"""
    # Get search query
    search_query = request.args.get('search', '').strip()
    
    # Base queries for each role
    students_query = User.query.filter_by(role='student')
    faculty_query = User.query.filter_by(role='faculty')
    admins_query = User.query.filter_by(role='admin')
    
    # Apply search filter if query exists
    if search_query:
        search_filter = User.first_name.ilike(f'%{search_query}%') | \
                       User.last_name.ilike(f'%{search_query}%') | \
                       User.middle_name.ilike(f'%{search_query}%') | \
                       User.username.ilike(f'%{search_query}%') | \
                       User.email.ilike(f'%{search_query}%')
        
        students_query = students_query.filter(search_filter)
        faculty_query = faculty_query.filter(search_filter)
        admins_query = admins_query.filter(search_filter)
    
    # Sort by last name, then first name
    students = students_query.order_by(User.last_name, User.first_name).all()
    faculty = faculty_query.order_by(User.last_name, User.first_name).all()
    admins = admins_query.order_by(User.last_name, User.first_name).all()
    
    return render_template('admin/crud/users.html', 
                         students=students,
                         faculty=faculty,
                         admins=admins,
                         search_query=search_query)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add a new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        year_level = request.form.get('year_level')
        department_id = request.form.get('department_id') or None
        
        if username and first_name and last_name and email and password and role:
            try:
                user = User(
                    username=username,
                    first_name=first_name,
                    middle_name=middle_name if middle_name else None,
                    last_name=last_name,
                    email=email,
                    role=role
                )
                user.set_password(password)
                
                if role == 'student' and year_level:
                    user.year_level = int(year_level)
                
                if department_id:
                    user.department_id = int(department_id)
                
                db.session.add(user)
                db.session.commit()
                flash(f'User "{user.get_full_name()}" added successfully.', 'success')
                return redirect(url_for('admin.users'))
            except ValueError:
                flash('Invalid input values.', 'error')
        else:
            flash('Username, first name, last name, email, password, and role are required.', 'error')
    
    departments = Department.query.all()
    return render_template('admin/crud/add_user.html', departments=departments)

@admin_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    """Edit a user"""
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        role = request.form.get('role')
        year_level = request.form.get('year_level')
        department_id = request.form.get('department_id') or None
        password = request.form.get('password')
        
        if username and first_name and last_name and email and role:
            try:
                user.username = username
                user.first_name = first_name
                user.middle_name = middle_name if middle_name else None
                user.last_name = last_name
                user.email = email
                user.role = role
                
                if role == 'student' and year_level:
                    user.year_level = int(year_level)
                else:
                    user.year_level = None
                
                if department_id:
                    user.department_id = int(department_id)
                else:
                    user.department_id = None
                
                if password:
                    user.set_password(password)
                
                db.session.commit()
                flash(f'User "{user.get_full_name()}" updated successfully.', 'success')
                return redirect(url_for('admin.users'))
            except ValueError:
                flash('Invalid input values.', 'error')
        else:
            flash('Username, first name, last name, email, and role are required.', 'error')
    
    departments = Department.query.all()
    return render_template('admin/crud/edit_user.html', user=user, departments=departments)

@admin_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    """Delete a user"""
    user = User.query.get_or_404(id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    # Check if user has enrollments or taught courses
    if user.enrollments.count() > 0:
        flash('Cannot delete user with existing enrollments.', 'error')
        return redirect(url_for('admin.users'))
    
    if user.taught_courses.count() > 0:
        flash('Cannot delete faculty with assigned courses.', 'error')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{user.username}" deleted successfully.', 'success')
    return redirect(url_for('admin.users'))

# Hierarchy View
@admin_bp.route('/department/<int:id>')
@login_required
@admin_required
def department_hierarchy(id):
    """View department hierarchy: courses -> faculty -> students"""
    department = Department.query.get_or_404(id)
    courses = Course.query.filter_by(department_id=id).all()
    
    hierarchy_data = []
    for course in courses:
        faculty = User.query.get(course.faculty_id) if course.faculty_id else None
        enrollments = Enrollment.query.filter_by(course_id=course.id).all()
        students = [User.query.get(e.student_id) for e in enrollments]
        
        hierarchy_data.append({
            'course': course,
            'faculty': faculty,
            'students': students,
            'enrollment_count': len(students)
        })
    
    return render_template('admin/department_hierarchy.html',
                         department=department,
                         hierarchy_data=hierarchy_data)

# Grade Management
@admin_bp.route('/grades')
@login_required
@admin_required
def grades():
    """View and manage all grades"""
    enrollments = Enrollment.query.all()
    return render_template('admin/grades.html', enrollments=enrollments)

@admin_bp.route('/grades/<int:enrollment_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_grade(enrollment_id):
    """Edit a grade (admin override)"""
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    try:
        grade = int(request.form.get('grade'))
        if grade < 1 or grade > 5:
            flash('Grade must be between 1 and 5.', 'error')
            return redirect(url_for('admin.grades'))
        
        enrollment.grade = str(grade)
        db.session.commit()
        
        student = User.query.get(enrollment.student_id)
        course = Course.query.get(enrollment.course_id)
        flash(f'Grade {grade} assigned to {student.username} for {course.name}', 'success')
        
    except (ValueError, TypeError):
        flash('Invalid grade value.', 'error')
    
    return redirect(url_for('admin.grades'))

# CSV Export
@admin_bp.route('/export/enrollments')
@login_required
@admin_required
def export_enrollments():
    """Export all enrollments to CSV"""
    enrollments = Enrollment.query.all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student', 'Course Code', 'Course Name', 'Department', 'Grade', 'Enrollment Date'])
    
    for enrollment in enrollments:
        student = User.query.get(enrollment.student_id)
        course = Course.query.get(enrollment.course_id)
        grade = enrollment.grade if enrollment.grade else 'Not Graded'
        dept_name = course.department.name if course.department else 'N/A'
        writer.writerow([
            student.username,
            course.code,
            course.name,
            dept_name,
            grade,
            enrollment.enrolled_at.strftime('%Y-%m-%d')
        ])
    
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=all_enrollments.csv'
    }

# Database Management
@admin_bp.route('/wipe-database', methods=['GET', 'POST'])
@login_required
@admin_required
def wipe_database():
    """Wipe all database data except the current admin user"""
    if request.method == 'POST':
        try:
            # Get current admin user info before deletion
            admin_username = current_user.username
            admin_email = current_user.email
            admin_password_hash = current_user.password_hash
            admin_first_name = current_user.first_name
            admin_middle_name = current_user.middle_name
            admin_last_name = current_user.last_name
            admin_role = current_user.role
            
            # Delete all data except current admin
            # Delete all enrollments first (foreign key constraints)
            Enrollment.query.delete()
            
            # Delete all courses
            Course.query.delete()
            
            # Delete all users except current admin
            User.query.filter(User.id != current_user.id).delete()
            
            # Delete all departments
            Department.query.delete()
            
            # Commit the deletions
            db.session.commit()
            
            flash('Database has been wiped successfully. All data has been removed except your admin account.', 'success')
            return redirect(url_for('admin.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while wiping the database: {str(e)}', 'error')
            return redirect(url_for('admin.wipe_database'))
    
    # GET request - show confirmation page
    # Get counts for confirmation display
    total_students = User.query.filter_by(role='student').count()
    total_faculty = User.query.filter_by(role='faculty').count()
    total_courses = Course.query.count()
    total_departments = Department.query.count()
    total_enrollments = Enrollment.query.count()
    
    return render_template('admin/wipe_database.html',
                         total_students=total_students,
                         total_faculty=total_faculty,
                         total_courses=total_courses,
                         total_departments=total_departments,
                         total_enrollments=total_enrollments)