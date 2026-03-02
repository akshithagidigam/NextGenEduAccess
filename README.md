🎓 NextGen EduAccess
AI-Powered Educational Management System

A Flask-based web application that modernizes academic management using:

🤖 AI-powered assignment analysis

🧠 Plagiarism detection

📅 Attendance tracking

📊 Performance analytics

💬 Real-time communication

📁 Project Structure

nextgen_eduaccess/
│
├── app.py                      # Main Flask application (routes + logic)
├── ai_detector.py              # AI content detection (Supabase Edge Function)
├── pdf_utils.py                # PDF text extraction utility
├── reset_db.py                 # Database initialization/reset script
├── nextgenedu.db               # SQLite database
├── .env                        # Environment variables (secrets)
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
🚀 Quick Start Guide
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

Secure subject-based login

Period-wise attendance marking

Duplicate attendance prevention

Marks entry (Mid-1, Mid-2, Semester)

Automatic grade & result calculation

Assignment creation with due dates

🤖 AI-generated content detection

🔍 Peer plagiarism detection

🚨 Automatic fail-alert email notifications

View student absence reasons

💬 Real-time messaging system

📊 Class performance analytics dashboard

👨‍🎓 Student Portal

Secure UID-based login

Dashboard with pending assignments

Period-wise attendance view

Absence reason submission

Subject-wise marks display

Assignment submission (PDF or Text)

📘 Quiz Modules

Computer Networks

Python

DBMS

Cryptography

Additional Features:

Quiz performance tracking

Timetable view

Messaging with teachers

🤖 AI & Detection Engine
AI Content Detection

Integrated with Supabase Edge Function

Returns AI confidence score

Provides AI usage verdict

Plagiarism Detection

TF-IDF Vectorization

Cosine Similarity comparison

Peer-to-peer submission matching

Relevance scoring vs assignment description

📊 Analytics Features

Class average, minimum & maximum marks

Pass / Fail distribution

Grade distribution per subject

Quiz progression tracking

Assignment submission analysis

🗄️ Database Design

Database Used: SQLite (nextgenedu.db)

Tables

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

🛡️ Security Features

Secure authentication system

Role-based access control

Environment variable protection

Duplicate attendance validation

Controlled file uploads

📌 License

Developed for academic and educational purposes only.
