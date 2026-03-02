🎓 NextGen EduAccess — AI-Powered Educational Management System

A Flask-based web application that modernizes academic management using AI-driven assignment analysis, plagiarism detection, attendance tracking, performance analytics, and real-time communication.

📁 Project Structure
nextgen_eduaccess/
├── app.py                      # Main Flask application (routes + business logic)
├── ai_detector.py              # AI content detection (Supabase Edge Function)
├── pdf_utils.py                # PDF text extraction utility
├── reset_db.py                 # Database initialization/reset script
├── nextgenedu.db               # SQLite database
├── .env                        # Environment variables (secrets)
│
├── templates/                  # Jinja2 HTML templates
│   ├── teacher_dashboard.html
│   ├── student_dashboard.html
│   ├── assignments.html
│   ├── quiz.html
│   └── ...
│
├── static/
│   ├── css/responsive.css      # Custom responsive styling
│   └── logo.png
│
└── uploads/                    # Student assignment PDF uploads
🚀 Quick Start
Step 1 — Install Dependencies
pip install flask python-dotenv scikit-learn requests pdfplumber
Step 2 — Configure Environment Variables

Create a .env file in the project root:

SECRET_KEY=your_secret_key
EMAIL_USER=your_gmail_address
EMAIL_PASS=your_gmail_app_password
DETECT_API_URL=your_supabase_edge_function_url
SUPABASE_ANON_KEY=your_supabase_anon_key
Step 3 — Initialize Database
python reset_db.py
Step 4 — Run the Application
python app.py

Open in browser:

http://localhost:5000
👥 User Roles
👩‍🏫 Teacher Portal

Secure login (subject-scoped access)

Period-wise attendance marking

Duplicate attendance prevention

Marks entry (Mid-1, Mid-2, Semester)

Automatic grade calculation

Assignment creation with due dates

AI-generated content detection

Peer plagiarism detection

Automatic fail-alert email notifications

View student absence reasons

Real-time messaging system

Class analytics dashboard

👨‍🎓 Student Portal

Secure login (UID-based)

Dashboard with pending assignments

Period-wise attendance view

Absence reason submission

Subject-wise marks with grade & result

Assignment submission (PDF/Text)

Subject-based quizzes:

Computer Networks

Python

DBMS

Cryptography

Quiz performance tracking

Timetable view

Messaging with teachers

🤖 AI & Detection Engine
1️⃣ AI Content Detection

Integrated with Supabase Edge Function

Returns:

AI confidence score

Verdict (AI-generated / Human-written)

2️⃣ Plagiarism Detection

TF-IDF Vectorization

Cosine Similarity comparison

Peer-to-peer submission comparison

Relevance scoring vs assignment description

📊 Analytics Features

Class average, min, max marks

Pass / Fail distribution

Grade distribution per subject

Quiz progression tracking

Assignment submission analysis

🗄️ Database Overview

Main tables used:

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

All data stored in SQLite (nextgenedu.db).

📌 Academic Features Analyzed

Period-wise attendance tracking

Mid-term & Semester exam scoring

Automatic result classification (PASS/FAIL)

Assignment AI detection score

Plagiarism similarity percentage

Quiz attempt history & progression

Student-teacher communication logs
