🎓 NextGen EduAccess
AI-Powered Educational Management Platform

NextGen EduAccess is a Flask-based Educational Management System designed to modernize academic workflows. It centralizes attendance management, performance tracking, AI-based assignment evaluation, quizzes, messaging, and analytics into a single web platform.

The system supports two primary roles:

Teachers – Manage attendance, marks, assignments, and student communication.

Students – View academic data, submit assignments, attempt quizzes, and message teachers.

🚀 Project Overview

NextGen EduAccess improves transparency, reduces manual errors, and enhances academic monitoring through a secure, role-based web application.

The platform includes:

Period-wise attendance tracking

Automated grade calculation

AI-based assignment detection

Plagiarism checking

Email alerts for failures

Real-time messaging

Subject-wise quiz system

Performance analytics dashboard

🛠️ Technology Stack
Backend

Python

Flask (Routing, Session Management, Business Logic)

Database

SQLite (nextgenedu.db)

Frontend

HTML

Jinja2 Templates

Styling

Custom CSS (responsive.css)

AI & Detection

Supabase Edge Function (AI-generated content detection)

scikit-learn (TF-IDF & Cosine Similarity for plagiarism detection)

Utilities

pdfplumber (PDF text extraction)

smtplib (Email notifications)

python-dotenv (.env configuration management)

✨ Core Features
👩‍🏫 Teacher Portal

Secure login with subject-scoped access

Dashboard with student list and timetable

Period-wise attendance marking (duplicate prevention)

Marks entry for Mid-1, Mid-2, Semester

Automatic grade and result calculation

Assignment creation with due dates and max marks

Assignment evaluation panel with:

AI detection score

Relevance score

Plagiarism score

Automatic fail-alert emails to parents

View absence reasons submitted by students

Real-time messaging with students

Class analytics (pass/fail, average, grade distribution)

👨‍🎓 Student Portal

Secure login using UID and password

Dashboard with pending assignment count

Personal attendance view (period-wise)

Absence reason submission

Subject-wise marks with grade and result

Assignment submission via PDF upload or text entry

Quiz modules for:

Computer Networks

Python

DBMS

Cryptography

Quiz performance tracking and score progression

Timetable view

Messaging with teachers

🤖 AI & Analytics Module

The system integrates intelligent analysis features:

AI-generated content detection using Supabase Edge Function

TF-IDF cosine similarity scoring for relevance

Peer plagiarism detection (student vs student comparison)

Subject-wise grade distribution analysis

Class-level performance metrics (average, min, max, pass ratio)

🗄️ Database Schema Overview

The application uses SQLite with the following key tables:

students

teachers

subjects

timetable

attendance

absence_reasons

student_marks

assignments

student_assignments

questions

quiz_attempts

messages

All data is securely stored in the nextgenedu.db database.

⚙️ Installation & Setup
✅ Prerequisites

Python 3.10+

pip

Gmail account with App Password enabled

Supabase project with deployed detect-text Edge Function

📦 Installation Steps
1️⃣ Clone the Project

git clone <repository-url>
cd nextgen-eduaccess

2️⃣ Install Dependencies

pip install flask python-dotenv scikit-learn requests pdfplumber

3️⃣ Create .env File in Root Directory

Add the following variables:

SECRET_KEY=your_secret_key
EMAIL_USER=your_gmail_address
EMAIL_PASS=your_gmail_app_password
DETECT_API_URL=your_supabase_edge_function_url
SUPABASE_ANON_KEY=your_supabase_anon_key

4️⃣ Initialize Database

python reset_db.py

5️⃣ Run the Application

python app.py

6️⃣ Open in Browser

http://localhost:5000

📂 Project Structure

NextGenEduAccess/
│
├── app.py
├── ai_detector.py
├── pdf_utils.py
├── reset_db.py
├── nextgenedu.db
├── .env
│
├── templates/
│ ├── teacher_dashboard.html
│ ├── student_dashboard.html
│ └── other HTML files
│
├── static/
│ ├── css/responsive.css
│ └── logo.png
│
└── uploads/

License

This project is developed for academic and educational purposes.
