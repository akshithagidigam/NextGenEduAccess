NextGen EduAccess
AI-Powered Educational Management Platform


1. Project Overview
NextGen EduAccess is a Flask-based web application designed to modernize the academic experience for students and teachers. The system centralizes attendance management, academic performance tracking, assignment submission with AI-detection, real-time messaging, and subject-based quizzes into a single cohesive platform.

The platform serves two primary user roles:
•	Teachers — manage attendance, enter marks, create and evaluate assignments, and communicate with students.
•	Students — view their academic data, submit assignments, attempt subject quizzes, and message teachers.

2. Technology Stack
Layer	Technology	Purpose
Backend	Python / Flask	Web server, routing, session management
Database	SQLite (nextgenedu.db)	Persistent data storage
Frontend	HTML / Jinja2 Templates	Server-rendered UI pages
Styling	Custom CSS (responsive.css)	Responsive layout and design
AI Detection	Supabase Edge Function	Detects AI-generated assignment content
Plagiarism Check	scikit-learn (TF-IDF)	Cosine similarity for submission comparison
PDF Handling	pdf_utils.py	Text extraction from student PDFs
Email Alerts	smtplib / Gmail SMTP	Absence & failure notifications to parents
Environment Config	.env / python-dotenv	Secrets management

3. Core Features
3.1 Teacher Portal
•	Secure login with subject-scoped sessions
•	Dashboard with student list and personal timetable
•	Attendance marking by period with duplicate prevention
•	Marks entry for Mid-1, Mid-2, and Semester exams with auto grade calculation
•	Assignment creation with due dates, descriptions, and max marks
•	Assignment evaluation panel: AI score, relevance score, plagiarism score per student
•	Automated fail-alert emails to parent on FAIL result
•	View absence reasons submitted by students
•	WhatsApp-style real-time messaging with all students

3.2 Student Portal
•	Secure login with UID and password
•	Dashboard with per-subject assignment pending counts
•	Personal attendance view (period-by-period) with absence reason submission
•	Subject-wise marks table with grade points and result
•	Assignment submission via PDF upload or text entry
•	Quiz module for Computer Networks, Python, DBMS, Cryptography
•	Performance charts showing quiz score progression over attempts
•	Timetable view showing all subjects and teachers
•	Messaging with teachers

3.3 AI & Analytics
•	AI-generated content detection via Supabase edge function (returns verdict + confidence score)
•	TF-IDF cosine similarity for relevance scoring (submission vs. assignment brief)
•	Peer plagiarism detection: compares each submission against all others for same assignment
•	Class analytics: pass/fail counts, average/max/min marks, grade distribution per subject

4. Database Schema
The application uses SQLite with the following key tables:

Table	Key Columns	Purpose
students	id, uid, name, class, email, password	Student accounts
teachers	id, name, username, password, subject_code, subject_name	Teacher accounts
subjects	subject_code, subject_name, type, credits	Curriculum subjects
timetable	day, period, subject_code, teacher_id	Class schedule
attendance	student_id, date, period1–period6	Daily period-wise attendance
absence_reasons	student_id, teacher_id, date, period, reason	Student absence justifications
student_marks	student_uid, subject_code, mid1/mid2/sem marks, result	Academic marks
assignments	subject_code, title, description, due_date, max_marks	Assignment records
student_assignments	assignment_id, student_uid, submission_file, ai_score, similarity_score	Submissions
questions	subject, question, options A–D, correct_option	Quiz question bank
quiz_attempts	student_id, subject, score, date_taken	Quiz history
messages	sender/receiver type+id, message, is_read, created_at	In-app chat

5. Installation & Setup
5.1 Prerequisites
•	Python 3.10+
•	pip (Python package manager)
•	A Gmail account with App Password enabled (for email alerts)
•	Supabase project with the detect-text edge function deployed

5.2 Installation Steps
1.	Clone or extract the project folder.
2.	Install Python dependencies:
3.	Run: pip install flask python-dotenv scikit-learn requests pdfplumber
4.	Create a .env file in the project root with the following keys:

Variable	Description
SECRET_KEY	Flask session secret key
EMAIL_USER	Gmail address for sending alerts
EMAIL_PASS	Gmail App Password (not your login password)
DETECT_API_URL	Supabase edge function URL for AI detection
SUPABASE_ANON_KEY	Supabase anonymous API key

5.	Initialize or reset the database using: python reset_db.py
6.	Start the application: python app.py
7.	Open the browser and navigate to: http://localhost:5000

6. Project Structure
File / Folder	Description
app.py	Main Flask application — all routes and business logic
ai_detector.py	AI text detection via Supabase edge function
pdf_utils.py	PDF text extraction utility
reset_db.py	Database initialization / reset script
nextgenedu.db	SQLite database file
.env	Environment variables (secrets — do not commit to version control)
templates/	HTML Jinja2 templates for all pages
static/css/responsive.css	Custom responsive stylesheet
static/logo.png	Application logo
uploads/	Uploaded student assignment PDFs

