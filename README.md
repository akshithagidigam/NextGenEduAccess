🎓 NextGen EduAccess

AI-Powered Educational Management Platform built with Flask

NextGen EduAccess is a role-based academic management system that integrates attendance tracking, performance monitoring, AI-based assignment evaluation, plagiarism detection, quizzes, analytics, and real-time messaging into one centralized web application.

📌 Table of Contents

Overview

Features

System Architecture

Technology Stack

Project Structure

Installation

Environment Variables

Database Schema

AI & Analytics Engine

Security

Future Improvements

License

📖 Overview

NextGen EduAccess is designed to digitize academic workflows for institutions by providing:

Centralized attendance management

Automated grading system

AI-based assignment verification

Plagiarism detection

Email notifications

Subject-wise quizzes

Academic performance analytics

Real-time teacher–student communication

The platform supports two primary user roles:

Teacher

Student

✨ Features
👩‍🏫 Teacher Portal

Secure login (subject-scoped)

Period-wise attendance marking

Duplicate attendance prevention

Marks entry (Mid-1, Mid-2, Semester)

Automatic grade calculation

Assignment creation with due dates

AI detection score per submission

Peer plagiarism detection

Fail-alert email notifications to parents

View student absence reasons

Real-time messaging system

Class performance analytics dashboard

👨‍🎓 Student Portal

Secure UID-based login

Dashboard with pending assignment counter

Personal attendance tracking

Absence reason submission

Subject-wise marks display

Assignment submission (PDF or Text)

Quiz modules:

Computer Networks

Python

DBMS

Cryptography

Quiz score progression tracking

Timetable view

Messaging with teachers

🏗️ System Architecture

Client (Browser)
⬇
Flask Application (app.py)
⬇
SQLite Database (nextgenedu.db)
⬇
AI Services:

Supabase Edge Function (AI detection)

TF-IDF + Cosine Similarity (Plagiarism)

🛠 Technology Stack
Layer	Technology	Purpose
Backend	Python + Flask	Routing, sessions, business logic
Database	SQLite	Persistent data storage
Frontend	HTML + Jinja2	Server-rendered UI
Styling	Custom CSS	Responsive layout
AI Detection	Supabase Edge Function	Detect AI-generated text
Plagiarism	scikit-learn (TF-IDF)	Similarity scoring
PDF Handling	pdfplumber	Extract text from PDFs
Email Alerts	smtplib (Gmail SMTP)	Automated notifications
Config	python-dotenv	Environment variable management
📁 Project Structure
nextgen_eduaccess/
├── app.py
├── ai_detector.py
├── pdf_utils.py
├── reset_db.py
├── nextgenedu.db
├── .env
│
├── templates/
│   ├── teacher_dashboard.html
│   ├── student_dashboard.html
│   ├── assignments.html
│   ├── quiz.html
│   └── ...
│
├── static/
│   ├── css/responsive.css
│   └── logo.png
│
└── uploads/
🚀 Installation
1️⃣ Clone the Repository
git clone <repository-url>
cd nextgen-eduaccess
2️⃣ Install Dependencies
pip install flask python-dotenv scikit-learn requests pdfplumber
3️⃣ Configure Environment Variables

Create a .env file:

SECRET_KEY=your_secret_key
EMAIL_USER=your_gmail_address
EMAIL_PASS=your_gmail_app_password
DETECT_API_URL=your_supabase_edge_function_url
SUPABASE_ANON_KEY=your_supabase_anon_key
4️⃣ Initialize Database
python reset_db.py
5️⃣ Run the Application
python app.py

Open in browser:

http://localhost:5000
🗄 Database Schema

Main tables:

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

Database: SQLite (nextgenedu.db)

🤖 AI & Analytics Engine
AI Content Detection

Supabase Edge Function integration

Returns AI confidence score and verdict

Plagiarism Detection

TF-IDF vectorization

Cosine similarity scoring

Peer submission comparison

Academic Analytics

Pass/Fail distribution

Grade distribution

Average / Min / Max marks

Quiz progression tracking
