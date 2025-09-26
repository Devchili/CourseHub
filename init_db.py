#!/usr/bin/env python3
"""
Database initialization script for Course Management System
Creates demo departments, courses, and users for testing
"""

from app import create_app
from extensions import db
from models import User, Department, Course, Enrollment
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create departments
        cs_dept = Department(name='Computer Science')
        math_dept = Department(name='Mathematics')
        eng_dept = Department(name='Engineering')
        business_dept = Department(name='Business Administration')
        
        db.session.add_all([cs_dept, math_dept, eng_dept, business_dept])
        db.session.commit()
        
        # Create users
        admin = User(
            username='admin',
            first_name='System',
            last_name='Administrator',
            email='admin@coursehub.edu',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        
        faculty1 = User(
            username='faculty1',
            first_name='John',
            middle_name='Michael',
            last_name='Smith',
            email='john.smith@coursehub.edu',
            password_hash=generate_password_hash('faculty123'),
            role='faculty',
            department_id=cs_dept.id
        )
        
        faculty2 = User(
            username='faculty2',
            first_name='Sarah',
            last_name='Johnson',
            email='sarah.johnson@coursehub.edu',
            password_hash=generate_password_hash('faculty123'),
            role='faculty',
            department_id=math_dept.id
        )
        
        faculty3 = User(
            username='faculty3',
            first_name='Robert',
            middle_name='David',
            last_name='Wilson',
            email='robert.wilson@coursehub.edu',
            password_hash=generate_password_hash('faculty123'),
            role='faculty',
            department_id=eng_dept.id
        )
        
        faculty4 = User(
            username='faculty4',
            first_name='Maria',
            last_name='Garcia',
            email='maria.garcia@coursehub.edu',
            password_hash=generate_password_hash('faculty123'),
            role='faculty',
            department_id=business_dept.id
        )
        
        student1 = User(
            username='student1',
            first_name='Alex',
            middle_name='James',
            last_name='Brown',
            email='alex.brown@coursehub.edu',
            password_hash=generate_password_hash('student123'),
            role='student',
            year_level=2,
            department_id=cs_dept.id
        )
        
        student2 = User(
            username='student2',
            first_name='Emily',
            last_name='Davis',
            email='emily.davis@coursehub.edu',
            password_hash=generate_password_hash('student123'),
            role='student',
            year_level=1,
            department_id=cs_dept.id
        )
        
        student3 = User(
            username='student3',
            first_name='Michael',
            middle_name='Thomas',
            last_name='Miller',
            email='michael.miller@coursehub.edu',
            password_hash=generate_password_hash('student123'),
            role='student',
            year_level=3,
            department_id=math_dept.id
        )
        
        student4 = User(
            username='student4',
            first_name='Jessica',
            last_name='Taylor',
            email='jessica.taylor@coursehub.edu',
            password_hash=generate_password_hash('student123'),
            role='student',
            year_level=1,
            department_id=math_dept.id
        )
        
        student5 = User(
            username='student5',
            first_name='David',
            middle_name='Robert',
            last_name='Anderson',
            email='david.anderson@coursehub.edu',
            password_hash=generate_password_hash('student123'),
            role='student',
            year_level=2,
            department_id=eng_dept.id
        )
        
        db.session.add_all([admin, faculty1, faculty2, faculty3, faculty4, student1, student2, student3, student4, student5])
        db.session.commit()
        
        # Create courses
        cs101 = Course(
            code='CS101',
            name='Introduction to Computer Science',
            year_required=1,
            semester='1st',
            is_ready=True,
            department_id=cs_dept.id,
            faculty_id=faculty1.id
        )
        
        cs102 = Course(
            code='CS102',
            name='Programming Fundamentals',
            year_required=1,
            semester='2nd',
            is_ready=True,
            department_id=cs_dept.id,
            prerequisite_id=None,
            faculty_id=faculty1.id
        )
        
        cs201 = Course(
            code='CS201',
            name='Data Structures and Algorithms',
            year_required=2,
            semester='1st',
            is_ready=True,
            department_id=cs_dept.id,
            prerequisite_id=1,  # CS101
            faculty_id=faculty1.id
        )
        
        cs202 = Course(
            code='CS202',
            name='Object-Oriented Programming',
            year_required=2,
            semester='2nd',
            is_ready=True,
            department_id=cs_dept.id,
            prerequisite_id=1,  # CS101
            faculty_id=faculty1.id
        )
        
        math101 = Course(
            code='MATH101',
            name='Calculus I',
            year_required=1,
            semester='1st',
            is_ready=True,
            department_id=math_dept.id,
            faculty_id=faculty2.id
        )
        
        math201 = Course(
            code='MATH201',
            name='Linear Algebra',
            year_required=2,
            semester='1st',
            is_ready=True,
            department_id=math_dept.id,
            prerequisite_id=5,  # MATH101
            faculty_id=faculty2.id
        )
        
        math202 = Course(
            code='MATH202',
            name='Discrete Mathematics',
            year_required=2,
            semester='2nd',
            is_ready=True,
            department_id=math_dept.id,
            prerequisite_id=5,  # MATH101
            faculty_id=faculty2.id
        )
        
        eng101 = Course(
            code='ENG101',
            name='Engineering Fundamentals',
            year_required=1,
            semester='1st',
            is_ready=True,
            department_id=eng_dept.id,
            faculty_id=faculty3.id
        )
        
        eng201 = Course(
            code='ENG201',
            name='Engineering Design',
            year_required=2,
            semester='1st',
            is_ready=True,
            department_id=eng_dept.id,
            prerequisite_id=8,  # ENG101
            faculty_id=faculty3.id
        )
        
        bus101 = Course(
            code='BUS101',
            name='Introduction to Business',
            year_required=1,
            semester='1st',
            is_ready=True,
            department_id=business_dept.id,
            faculty_id=faculty4.id
        )
        
        bus201 = Course(
            code='BUS201',
            name='Business Management',
            year_required=2,
            semester='1st',
            is_ready=True,
            department_id=business_dept.id,
            prerequisite_id=10,  # BUS101
            faculty_id=faculty4.id
        )
        
        db.session.add_all([cs101, cs102, cs201, cs202, math101, math201, math202, eng101, eng201, bus101, bus201])
        db.session.commit()
        
        # Create enrollments with various scenarios
        # Student 1 (CS Year 2): Passed CS101, In Progress CS201, Failed CS202 (eligible for retake)
        enrollment1 = Enrollment(student_id=student1.id, course_id=cs101.id, grade='2.0', enrolled_at=datetime(2023, 9, 1))
        enrollment2 = Enrollment(student_id=student1.id, course_id=cs201.id, grade=None, enrolled_at=datetime(2024, 1, 15))
        enrollment3 = Enrollment(student_id=student1.id, course_id=cs202.id, grade='4.0', enrolled_at=datetime(2024, 1, 15))
        
        # Student 2 (CS Year 1): In Progress CS101
        enrollment4 = Enrollment(student_id=student2.id, course_id=cs101.id, grade=None, enrolled_at=datetime(2024, 1, 15))
        
        # Student 3 (Math Year 3): Passed MATH101, Passed MATH201
        enrollment5 = Enrollment(student_id=student3.id, course_id=math101.id, grade='1.5', enrolled_at=datetime(2022, 9, 1))
        enrollment6 = Enrollment(student_id=student3.id, course_id=math201.id, grade='2.25', enrolled_at=datetime(2023, 9, 1))
        
        # Student 4 (Math Year 1): In Progress MATH101
        enrollment7 = Enrollment(student_id=student4.id, course_id=math101.id, grade=None, enrolled_at=datetime(2024, 1, 15))
        
        # Student 5 (Engineering Year 2): Passed ENG101, In Progress ENG201
        enrollment8 = Enrollment(student_id=student5.id, course_id=eng101.id, grade='3.0', enrolled_at=datetime(2023, 9, 1))
        enrollment9 = Enrollment(student_id=student5.id, course_id=eng201.id, grade=None, enrolled_at=datetime(2024, 1, 15))
        
        # Add some incomplete grades for testing
        enrollment10 = Enrollment(student_id=student1.id, course_id=cs102.id, grade='INC', enrolled_at=datetime(2023, 9, 1))
        
        db.session.add_all([
            enrollment1, enrollment2, enrollment3, enrollment4, enrollment5, 
            enrollment6, enrollment7, enrollment8, enrollment9, enrollment10
        ])
        db.session.commit()
        
        print("Database initialized successfully!")
        print("\nDemo Accounts:")
        print("=" * 50)
        print("Admin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Full Name: System Administrator")
        print()
        print("Faculty:")
        print("  Username: faculty1")
        print("  Password: faculty123")
        print("  Full Name: John Michael Smith (Computer Science)")
        print("  Username: faculty2")
        print("  Password: faculty123")
        print("  Full Name: Sarah Johnson (Mathematics)")
        print("  Username: faculty3")
        print("  Password: faculty123")
        print("  Full Name: Robert David Wilson (Engineering)")
        print("  Username: faculty4")
        print("  Password: faculty123")
        print("  Full Name: Maria Garcia (Business Administration)")
        print()
        print("Students:")
        print("  Username: student1")
        print("  Password: student123")
        print("  Full Name: Alex James Brown (CS Year 2)")
        print("  - Passed CS101 (2.0), In Progress CS201, Failed CS202 (4.0), Incomplete CS102")
        print()
        print("  Username: student2")
        print("  Password: student123")
        print("  Full Name: Emily Davis (CS Year 1)")
        print("  - In Progress CS101")
        print()
        print("  Username: student3")
        print("  Password: student123")
        print("  Full Name: Michael Thomas Miller (Math Year 3)")
        print("  - Passed MATH101 (1.5), Passed MATH201 (2.25)")
        print()
        print("  Username: student4")
        print("  Password: student123")
        print("  Full Name: Jessica Taylor (Math Year 1)")
        print("  - In Progress MATH101")
        print()
        print("  Username: student5")
        print("  Password: student123")
        print("  Full Name: David Robert Anderson (Engineering Year 2)")
        print("  - Passed ENG101 (3.0), In Progress ENG201")
        print()
        print("Key Features Demonstrated:")
        print("=" * 50)
        print("✅ New grading system with floating values (1.0, 1.25, 1.50, 1.75, etc.) and INC")
        print("✅ Course semester system (1st/2nd semester) and ready status")
        print("✅ Student name fields (first, middle, last) with alphabetical sorting")
        print("✅ Faculty re-enrollment for failed students (no automatic retake)")
        print("✅ Department restrictions and year level requirements")
        print("✅ Prerequisite checking with passing grade requirements")
        print("✅ Course status tracking (Passed, Failed, In Progress, Incomplete)")
        print("✅ Enhanced UI/UX with modern design and better organization")

if __name__ == '__main__':
    init_database()
