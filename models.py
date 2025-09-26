from extensions import db
from sqlalchemy import and_
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, faculty, student
    year_level = db.Column(db.Integer, nullable=True)  # For students only
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic')
    taught_courses = db.relationship('Course', backref='faculty', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_faculty(self):
        return self.role == 'faculty'
    
    def is_student(self):
        return self.role == 'student'
    
    def get_full_name(self):
        """Get the full name of the user"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def check_year_progression_eligibility(self):
        """Check if student is eligible for year progression and return progression info"""
        if not self.is_student() or not self.department_id or not self.year_level:
            return False, None, None

        # Get all 2nd semester courses for current year level in student's department
        # Students are promoted when they complete all 2nd semester courses of their current year
        current_year_2nd_sem_courses = Course.query.filter_by(
            department_id=self.department_id,
            year_required=self.year_level,
            semester='2nd'
        ).all()

        if not current_year_2nd_sem_courses:
            # No 2nd semester courses for current year, can't progress
            return False, None, None

        # Check completion status for each 2nd semester course
        incomplete_courses = []
        completed_courses = []

        for course in current_year_2nd_sem_courses:
            enrollment = Enrollment.query.filter_by(
                student_id=self.id,
                course_id=course.id
            ).first()

            if not enrollment or not enrollment.grade or enrollment.grade == 'INC':
                incomplete_courses.append(course)
            elif not enrollment.is_passing():
                incomplete_courses.append(course)
            else:
                completed_courses.append(course)

        # Check if all 2nd semester courses are completed
        if not incomplete_courses:
            # Student has completed all 2nd semester courses for current year
            next_year = self.year_level + 1

            # Check if there are courses available for next year
            next_year_courses = Course.query.filter_by(
                department_id=self.department_id,
                year_required=next_year
            ).first()

            if next_year_courses:
                return True, next_year, len(completed_courses)
            else:
                # No more courses available (student might be in final year)
                return False, None, len(completed_courses)

        return False, None, len(completed_courses)

    def are_all_current_semester_courses_graded(self, semester='1st'):
        """Check if ALL courses for the current semester have been enrolled in and graded"""
        if not self.is_student() or not self.department_id:
            return False

        # Get all courses for the specified semester in student's department and year level
        semester_courses = Course.query.filter_by(
            department_id=self.department_id,
            year_required=self.year_level,
            semester=semester
        ).all()

        if not semester_courses:
            # No courses for this semester, consider it as "graded"
            return True

        # Check that student is enrolled in ALL courses and they are all graded
        for course in semester_courses:
            enrollment = Enrollment.query.filter_by(
                student_id=self.id,
                course_id=course.id
            ).first()

            # If not enrolled in this course, return False
            if not enrollment:
                return False

            # If enrolled but no grade or incomplete grade, return False
            if enrollment.grade is None or enrollment.grade == 'INC':
                return False

            # If enrolled but failing grade, return False
            if not enrollment.is_passing():
                return False

        # If we get here, student is enrolled in ALL courses and they all have passing grades
        return True

    def promote_to_next_year(self):
        """Promote student to next year level"""
        if not self.is_student():
            return False, "User is not a student"

        eligible, next_year, completed_count = self.check_year_progression_eligibility()
        if eligible and next_year:
            old_year = self.year_level
            self.year_level = next_year
            return True, f"Promoted from Year {old_year} to Year {next_year}"

        return False, "Not eligible for year progression"

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Relationships
    courses = db.relationship('Course', backref='department', lazy='dynamic')
    # All users in this department
    users = db.relationship('User', lazy='dynamic', foreign_keys='User.department_id', backref='department')
    # View-only filtered relationship for faculty in this department
    faculty = db.relationship(
        'User',
        lazy='dynamic',
        primaryjoin=and_(id == User.department_id, User.role == 'faculty'),
        foreign_keys='User.department_id',
        viewonly=True
    )

course_prerequisite_association = db.Table(
    'course_prerequisite_association',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
    db.Column('prerequisite_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    year_required = db.Column(db.Integer, nullable=False, default=1)
    semester = db.Column(db.String(20), nullable=False, default='1st')  # 1st or 2nd semester
    is_ready = db.Column(db.Boolean, default=True)  # Whether the course is ready to take
    # Legacy single prerequisite support (kept for backward compatibility)
    prerequisite_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    # Legacy single prerequisite relationship
    prerequisite = db.relationship('Course', remote_side=[id], backref='legacy_dependent_courses')
    # New: multiple prerequisites relationship
    prerequisites = db.relationship(
        'Course',
        secondary=course_prerequisite_association,
        primaryjoin=(id == course_prerequisite_association.c.course_id),
        secondaryjoin=(id == course_prerequisite_association.c.prerequisite_id),
        backref=db.backref('dependent_courses', lazy='dynamic'),
        lazy='dynamic'
    )
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic')
    
    def is_eligible_for_student(self, student):
        """Check if a student is eligible for this course"""
        # Check if course is ready to take
        if not self.is_ready:
            return False, "Course is not currently available for enrollment"
        
        # Check if student is from the same department
        if student.department_id != self.department_id:
            return False, "Course is not available in your department"
        
        # Check year level requirement
        if student.year_level < self.year_required:
            return False, f"Year level requirement not met. You need to be in year {self.year_required} or higher"
        
        # Check if student has already passed this course
        existing_enrollment = Enrollment.query.filter_by(
            student_id=student.id,
            course_id=self.id
        ).first()
        
        if existing_enrollment and existing_enrollment.grade is not None and existing_enrollment.is_passing():
            return False, "You have already passed this course"
        
        # Note: Removed overly broad 2nd semester blocking logic.
        # Pre-requisite checking is now handled individually per course below.

        # Check if this is a course from a year level the student should have already completed
        # (unless they failed it and need to retake)
        if student.year_level > self.year_required:
            # Check if student has any failed courses from this year level that need retaking
            failed_courses_from_year = Enrollment.query.join(Course).filter(
                Enrollment.student_id == student.id,
                Course.year_required == self.year_required,
                Course.department_id == student.department_id,
                Enrollment.grade != 'INC',
                Enrollment.grade.isnot(None)
            ).all()

            # Filter for failed grades (> 3.0) in Python since we need to handle string-to-float conversion
            failed_courses_from_year = [e for e in failed_courses_from_year if not e.is_passing()]
            failed_courses_from_year = failed_courses_from_year[0] if failed_courses_from_year else None
            
            # If no failed courses from this year level, student shouldn't see courses from lower years
            if not failed_courses_from_year:
                return False, f"You should have already completed Year {self.year_required} courses"
        
        # Check prerequisites (supports multiple). If multiple are defined, require all to be passed.
        prereq_course_ids = []
        if self.prerequisites and self.prerequisites.count() > 0:
            prereq_course_ids = [c.id for c in self.prerequisites.all()]
        elif self.prerequisite_id:
            prereq_course_ids = [self.prerequisite_id]

        for prereq_id in prereq_course_ids:
            prerequisite_course = db.session.get(Course, prereq_id)
            prerequisite_enrollment = Enrollment.query.filter_by(
                student_id=student.id,
                course_id=prereq_id
            ).first()

            prereq_name = prerequisite_course.code if prerequisite_course else f"Course ID {prereq_id}"

            if not prerequisite_enrollment or prerequisite_enrollment.grade is None:
                return False, f"Cannot enroll in {self.code}. Pre-requisite {prereq_name} was not completed."
            if prerequisite_enrollment.grade == 'INC':
                return False, f"Cannot enroll in {self.code}. Pre-requisite {prereq_name} is incomplete - must complete prerequisite first."
            if not prerequisite_enrollment.is_passing():
                return False, f"Cannot enroll in {self.code}. Pre-requisite {prereq_name} was not met."
        
        return True, "Eligible for enrollment"

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.String(10), nullable=True)  # Support for 1.0, 1.25, 1.50, 1.75, 2.0, 2.25, 2.50, 2.75, 3.0, 3.25, 3.50, 3.75, 4.0, 5.0, INC
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure unique student-course combinations
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='unique_student_course'),)
    
    def is_passing(self):
        """Check if the grade is passing (≤ 3.0)"""
        if self.grade is None or self.grade == 'INC':
            return False
        try:
            grade_value = float(self.grade)
            # Passing for this scale is ≤ 3.00. 5.00 is failing.
            return grade_value <= 3.0
        except ValueError:
            return False
    
    def get_status(self):
        """Get the current status of the enrollment"""
        if self.grade is None:
            return "In Progress"
        elif self.grade == 'RET':
            return "Retaking"
        elif self.grade == 'INC':
            return "Incomplete"
        elif self.is_passing():
            return "Passed"
        else:
            return "Failed"
    
    def can_retake(self):
        """Check if the course can be retaken (failed grade or incomplete)"""
        if self.grade is None:
            return False
        # Do not allow re-enroll action while already marked as retaking
        if self.grade == 'RET':
            return False
        return self.grade == 'INC' or not self.is_passing()
