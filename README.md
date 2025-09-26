# CourseHub - Course Management System

A comprehensive Flask-based course management system with automatic semester and year progression for educational institutions.

## 🌟 Features

### 🎓 **Automatic Academic Progression**
- **Smart Semester Progression**: Students automatically see 2nd semester courses when all 1st semester courses are graded
- **Automatic Year Advancement**: Students are promoted to the next year when they complete all 2nd semester courses
- **Grade-Driven Logic**: Progression based on faculty grading completion, not manual settings

### 👥 **Multi-Role System**
- **Admin**: Complete system management, user creation, course management
- **Faculty**: Course assignment, student grading, grade management
- **Student**: Course enrollment, grade viewing, automatic progression

### 📚 **Course Management**
- **Department-Based Organization**: Courses organized by academic departments
- **Prerequisite System**: Advanced prerequisite handling with multiple dependencies
- **Year-Level Filtering**: Students only see courses appropriate for their academic year
- **Semester Organization**: Automatic 1st/2nd semester course display

### 📊 **Grade Management**
- **Numeric Grading System**: 1.0-5.0 scale with 3.0 as passing threshold
- **Grade Status Tracking**: Pass/Fail/Incomplete/Retake status management
- **Automatic Eligibility**: Course eligibility based on prerequisite completion

### 🔐 **Authentication & Access Control**
- **Secure Login**: Hashed passwords with Werkzeug security
- **Role-Based Access**: Admin, Faculty, Student with appropriate permissions
- **Session Management**: Flask-Login integration for secure sessions
- **Department Assignments**: Users properly assigned to academic departments

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Flask
- SQLAlchemy
- SQLite (default) or PostgreSQL/MySQL

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Devchili/CourseHub.git
cd CourseHub
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize the database**
```bash
python app.py
```

4. **Access the application**
- Open your browser to `http://localhost:5000`
- Default admin credentials will be created automatically

## 🎯 Core Functionality

### Academic Progression Flow

1. **New Student Registration**
   - Students start with Year 1, 1st semester courses
   - No manual semester settings required

2. **Semester Progression**
   - Complete all 1st semester courses → See 2nd semester courses
   - Automatic detection based on faculty grading

3. **Year Progression**
   - Complete all 2nd semester courses → Promoted to next year
   - Automatic advancement with congratulatory messages

### User Roles & Permissions

#### 👨‍💼 **Admin**
- Create and manage users (students, faculty, admin)
- Department management
- Course creation and assignment
- System-wide oversight and reporting
- Database management tools

#### 👨‍🏫 **Faculty**
- View assigned courses
- Grade student submissions
- Monitor student progress
- Course-specific student management

#### 👨‍🎓 **Student**
- View available courses for current year/semester
- Enroll in eligible courses
- Track academic progress
- Automatic progression notifications

## 📁 Project Structure

```
CourseHub/
├── app.py                 # Main application entry point
├── models.py              # Database models and business logic
├── extensions.py          # Flask extensions configuration
├── admin/                 # Admin blueprint
│   └── routes.py         # Admin routes and views
├── faculty/               # Faculty blueprint
│   └── routes.py         # Faculty routes and views
├── student/               # Student blueprint
│   └── routes.py         # Student routes and views
├── templates/             # Jinja2 templates
│   ├── admin/            # Admin interface templates
│   ├── faculty/          # Faculty interface templates
│   ├── student/          # Student interface templates
│   └── base.html         # Base template
├── static/               # Static files (CSS, JS, images)
└── tests/                # Test scripts and utilities
```

## 🛠️ Technical Features

### Database Models
- **User**: Multi-role user management with department assignments
- **Department**: Academic department organization
- **Course**: Comprehensive course information with prerequisites
- **Enrollment**: Student-course relationships with grading

### Advanced Prerequisites
- **Multiple Prerequisites**: Courses can have multiple prerequisite requirements
- **Legacy Support**: Backward compatibility with single prerequisite system
- **Automatic Validation**: Enrollment blocked until prerequisites are met

### Automatic Systems
- **Semester Detection**: Smart logic determines which semester courses to display
- **Year Progression**: Automatic promotion based on academic completion
- **Grade Validation**: Comprehensive grade checking and status management

## 📊 Sample Data

The system includes sample data for testing:
- **16 Year 1 Courses**: 8 first semester, 8 second semester
- **10 Year 2 Courses**: 5 first semester, 5 second semester
- **Realistic Prerequisites**: CC 103 requires CC 102, etc.
- **Sample Users**: Admin, faculty, and student accounts

## 🧪 Testing

Comprehensive test suite included:
```bash
# Test semester progression
python test_semester_progression.py

# Test year progression
python test_automatic_year_progression.py

# Test complete student flow
python test_complete_student_flow.py

# Verify existing students
python verify_existing_students.py
```

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV`: Set to 'development' for debug mode
- `DATABASE_URL`: Database connection string (optional)
- `SECRET_KEY`: Flask secret key for sessions

### Database Configuration
- Default: SQLite (`course_management.db`)
- Supports: PostgreSQL, MySQL, SQLite
- Automatic table creation on first run

## 📈 Recent Updates

### v2.0 - Automatic Progression System
- ✅ Implemented automatic semester progression
- ✅ Added automatic year advancement
- ✅ Enhanced prerequisite system
- ✅ Fixed department assignment display issues
- ✅ Added comprehensive test suite

### v1.0 - Core System
- ✅ Multi-role user management
- ✅ Course and department management
- ✅ Basic enrollment and grading
- ✅ Responsive web interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please open an issue on GitHub or contact the development team.

## 🙏 Acknowledgments

- Built with Flask and SQLAlchemy
- UI components from Tailwind CSS
- Icons from Heroicons
- Testing utilities included for comprehensive validation

---

**CourseHub** - Streamlining academic management with intelligent automation 🎓
