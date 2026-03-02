from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
import sqlite3
import os
import smtplib
from email.message import EmailMessage
from datetime import date
from dotenv import load_dotenv

# ---------------- CONFIG ----------------
load_dotenv()
app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_PATH = "nextgenedu.db"
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# ---------------- DB HELPER ----------------
# ---------------- DB HELPER ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")  # Enable foreign keys
    return conn

# Create questions table if not exists

def create_questions_table():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL
        )
    """)
    db.commit()
    db.close()
create_questions_table()
# ---------------- CREATE STUDENT MARKS TABLE ----------------
def create_student_marks_table():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS student_marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_uid TEXT NOT NULL,
            subject_code TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            credits INTEGER,
            mid1_marks real,
            mid2_marks real,
            sem_marks real,
            total_marks real,
            gradepoints REAL,
            result TEXT
          
        )
    """)
    db.commit()
    db.close()

create_student_marks_table()
# ---------------- CREATE SUBJECTS TABLE ----------------
def create_subjects_table():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_code TEXT UNIQUE NOT NULL,
            subject_name TEXT NOT NULL,
            type TEXT NOT NULL,  -- Theory or Practical
            credits INTEGER NOT NULL
        )
    """)
    db.commit()
    db.close()

create_subjects_table()


# ---------------- CREATE QUIZ ATTEMPTS TABLE ----------------
def create_quiz_attempts_table():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            score INTEGER NOT NULL,
            date_taken DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)
    db.commit()
    db.close()

create_quiz_attempts_table()
# ---------------- CREATE ASSIGNMENTS TABLE ----------------
def create_assignments_table():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_code TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date DATE NOT NULL,
            max_marks INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    db.close()
create_assignments_table()

def create_student_assignments_table():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS student_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER NOT NULL,
            student_uid TEXT NOT NULL,
            submitted INTEGER DEFAULT 0,
            ai_copied INTEGER DEFAULT 0,
            FOREIGN KEY(assignment_id) REFERENCES assignments(id),
            FOREIGN KEY(student_uid) REFERENCES students(uid),
            UNIQUE(assignment_id, student_uid)
        )
    """)
    db.commit()
    db.close()

create_student_assignments_table()

# 👇 ADD THIS FUNCTION AND CALL HERE 👇
def add_submission_text_column():
    db = get_db()
    try:
        db.execute("ALTER TABLE student_assignments ADD COLUMN submission_text TEXT")
        db.commit()

    except Exception as e:
        print("Column might already exist:", e)
    db.close()

add_submission_text_column()



# ---------------- HOME ----------------
@app.route("/")
def splash():
    return render_template("splash.html")


@app.route("/index")
def index():
    return render_template("index.html")

# ---------------- TEACHER LOGIN ----------------
@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, subject_code, subject_name
            FROM teachers
            WHERE username = ? AND password = ?
        """, (username, password))

        teacher = cur.fetchone()
        conn.close()

        if teacher:
            session['teacher_id'] = teacher['id']
            session['teacher_name'] = teacher['name']
            session['teacher_subject_code'] = teacher['subject_code']
            session['teacher_subject_name'] = teacher['subject_name']

            return redirect(url_for('teacher_dashboard'))
        else:
            flash("Invalid credentials")
            return redirect(url_for('teacher_login'))

    return render_template('teacher_login.html')

# ---------------- TEACHER DASHBOARD ----------------

@app.route('/teacher/dashboard')
def teacher_dashboard():
    # ---------------- CHECK LOGIN ----------------
    if 'teacher_subject_code' not in session:
        return redirect(url_for('teacher_login'))

    teacher_id = session.get('teacher_id')

    # ---------------- CONNECT DB ----------------
    db = get_db()
    cur = db.cursor()

    # ---------------- FETCH STUDENTS ----------------
    students = cur.execute("""
        SELECT uid, name, class, email, id 
        FROM students
    """).fetchall()
    
    # ---------------- FETCH TEACHER TIMETABLE ----------------
    timetable = cur.execute("""
        SELECT t.day, t.period, s.subject_name AS subject
        FROM timetable t
        JOIN subjects s ON t.subject_code = s.subject_code
        WHERE t.teacher_id = ?
        ORDER BY 
            CASE t.day
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
            END,
            t.period
    """, (teacher_id,)).fetchall()

    # ---------------- CLOSE DB ----------------
    db.close()

    # ---------------- RENDER DASHBOARD ----------------
    return render_template(
        'teacher_dashboard.html',
        students=students,
        timetable=timetable
    )

# ---------------- VIEW STUDENTS ----------------
@app.route('/teacher/students')
def teacher_students():
    if 'teacher_subject_code' not in session:
        return redirect(url_for('teacher_login'))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT uid, name, class, email
        FROM students
        ORDER BY uid
    """)
    students = cur.fetchall()
    conn.close()

    return render_template(
        'teacher_students.html',
        students=students
    )

# ---------------- MARK ATTENDANCE ----------------
# ---------------- MARK ATTENDANCE ----------------
from datetime import date, datetime

@app.route("/teacher/mark_attendance", methods=["GET", "POST"])
def mark_attendance():
    if "teacher_id" not in session:
        return redirect(url_for("teacher_login"))

    db = get_db()

    teacher_id = session["teacher_id"]
    today_date = date.today().strftime("%Y-%m-%d")

    # Fetch all students
    students = db.execute("SELECT * FROM students").fetchall()

    # Find teacher periods for today
    weekday = datetime.today().strftime("%A")
    teacher_periods_today = db.execute("""
        SELECT period FROM timetable
        WHERE day=? AND teacher_id=?
    """, (weekday, teacher_id)).fetchall()

    teacher_periods = [p["period"] for p in teacher_periods_today]

    # ---------------- POST LOGIC ----------------
    if request.method == "POST":
        attendance_date = request.form.get("attendance_date")
        selected_period = int(request.form.get("period"))

        # -------- Validations --------
        if not attendance_date:
            flash("Please select a date")
            return redirect(url_for("mark_attendance"))

        if attendance_date > today_date:
            flash("Cannot mark attendance for a future date!")
            return redirect(url_for("mark_attendance"))

        if selected_period not in teacher_periods:
            flash("You do not have class in the selected period!")
            return redirect(url_for("mark_attendance"))

        # -------- MAIN ATTENDANCE LOGIC --------
        for stu in students:
            sid = stu["uid"]
            val = request.form.get(
                f"attendance[{sid}][{selected_period}]", "P"
            )

            existing = db.execute(
                "SELECT * FROM attendance WHERE student_id=? AND date=?",
                (sid, attendance_date)
            ).fetchone()

            # ----- BLOCK duplicate marking -----
            if existing and existing[f"period{selected_period}"] is not None:
                flash(
                    f"Attendance already marked for Period "
                    f"{selected_period} on {attendance_date}"
                )
                db.close()
                return redirect(url_for("mark_attendance"))

            if existing:
                # Update only the selected period
                db.execute(f"""
                    UPDATE attendance
                    SET period{selected_period}=?
                    WHERE student_id=? AND date=?
                """, (val, sid, attendance_date))

            else:
                # Insert new row for this date
                periods = [None] * 6
                periods[selected_period - 1] = val

                db.execute("""
                    INSERT INTO attendance
                    (student_id, date, period1, period2, period3,
                     period4, period5, period6)
                    VALUES (?,?,?,?,?,?,?,?)
                """, (sid, attendance_date, *periods))

            # -------- Absent Mail (only once) --------
            if val == "A":
                send_absent_mail(
                    parent_email=stu["email"],
                    student_name=stu["name"],
                    absent_periods=[selected_period],
                    subject_name=session.get(
                        "teacher_subject_name", "Unknown Subject"
                    ),
                    attendance_date=attendance_date
                )

        db.commit()
        db.close()

        flash("Attendance saved successfully!")
        return redirect(url_for("teacher_dashboard"))

    # ---------------- GET REQUEST ----------------
    db.close()
    return render_template(
        "mark_attendance.html",
        students=students,
        today=today_date,
        teacher_periods=teacher_periods
    )


    # ---------------- STUDENT ATTENDANCE VIEW ----------------
@app.route('/student/attendance')
def student_attendance():
    if 'student_uid' not in session:
        return redirect(url_for('student_login'))

    student_id = session['student_uid']
    db = get_db()

    # Fetch attendance rows
    attendance_rows = db.execute("""
        SELECT * FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC
    """, (student_id,)).fetchall()

    attendance = []
    for row in attendance_rows:
        record = dict(row)
        record_date = record['date']
        record_teachers = {}

        # For each period, fetch teacher from timetable
        for i in range(1, 7):
            weekday = datetime.strptime(record_date, "%Y-%m-%d").strftime("%A")
            period = i
            t = db.execute("""
                SELECT teacher_id FROM timetable
                WHERE day=? AND period=? 
            """, (weekday, period)).fetchone()
            record_teachers[f'period{i}_teacher'] = t['teacher_id'] if t else None

        # merge teacher info into record
        record.update(record_teachers)
        attendance.append(record)

    db.close()

    return render_template(
        'student_attendance.html',
        attendance=attendance,
        total_present=sum(1 for r in attendance for p in ['period1','period2','period3','period4','period5','period6'] if r[p] == 'P'),
        total_absent=sum(1 for r in attendance for p in ['period1','period2','period3','period4','period5','period6'] if r[p] == 'A')
    )

# ---------------- SUBMIT ABSENCE REASON ----------------
@app.route('/student/submit_reason', methods=['POST'])
def submit_reason():
    if 'student_uid' not in session:
        return jsonify({'status':'error','msg':'Not logged in'})

    try:
        data = request.get_json()
        student_id = session['student_uid']
        teacher_id = data.get('teacher_id')
        date_val = data.get('date')
        period_val = data.get('period')
        reason_val = data.get('reason')

        if not all([date_val, period_val, reason_val, teacher_id]):
            return jsonify({'status':'error','msg':'Missing data'})

        db = get_db()
        db.execute("""
            INSERT INTO absence_reasons (student_id, teacher_id, date, period, reason, submitted_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (student_id, teacher_id, date_val, period_val, reason_val))
        db.commit()
        db.close()
        return jsonify({'status':'success'})

    except Exception as e:
        print("Submit reason error:", e)
        return jsonify({'status':'error','msg': str(e)})
    
    # ---------------- VIEW ABSENCE REASONS ----------------
@app.route('/teacher/absence_reasons')
def absence_reasons():
    if 'teacher_id' not in session:
        return redirect(url_for('teacher_login'))

    teacher_id = session['teacher_id']
    db = get_db()

    messages = db.execute("""
        SELECT
            s.name AS student_name,
            ar.date,
            ar.period,
            ar.reason,
            ar.submitted_at
        FROM absence_reasons ar
        JOIN students s ON ar.student_id = s.uid
        WHERE ar.teacher_id = ?
        ORDER BY ar.submitted_at DESC
    """, (teacher_id,)).fetchall()

    db.close()
    return render_template('absence_reasons.html', messages=messages)

# ---------------- EMAIL FUNCTION ----------------
def send_absent_mail(parent_email, student_name, attendance_date, absent_periods, subject_name):
    try:
        msg = EmailMessage()
        msg["Subject"] = f"Absence Alert - {student_name}"
        msg["From"] = EMAIL_USER
        msg["To"] = parent_email
        msg.set_content(f"""
Dear Parent,

Your child {student_name} was marked ABSENT on {attendance_date}.
Subject: {subject_name}
Absent Periods (Hours): {absent_periods}

Please contact the institution if needed.

contact:NextGenEdu@gmail.com
Regards,
NextGen EduAccess
        """)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
    except Exception as e:
        print("Email error:", e)

def send_marks_alert(parent_email, student_name, subject_name, total):
    try:
        msg = EmailMessage()
        msg["Subject"] = "⚠️ Semester Result Alert"
        msg["From"] = EMAIL_USER
        msg["To"] = parent_email

        msg.set_content(f"""
Dear Parent,

Your ward {student_name} has scored {total} marks in {subject_name}
and has FAILED (below 40%).

Please contact the college for further guidance.

Regards,
NextGen EduAccess
        """)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)

    except Exception as e:
        print("Marks email error:", e)





# ---------------- TEACHER MARKS ENTRY ----------------
@app.route("/teacher/marks", methods=["GET", "POST"])
def teacher_marks():
    if "teacher_id" not in session:
        return redirect(url_for("teacher_login"))

    db = get_db()
    subject_code = session.get("teacher_subject_code")
    subject_name = session.get("teacher_subject_name")

    students = db.execute(
        "SELECT uid, name, email FROM students ORDER BY uid"
    ).fetchall()

    rows = db.execute("""
        SELECT student_uid, mid1_marks, mid2_marks, sem_marks, alert_sent
        FROM student_marks
        WHERE subject_code = ?
    """, (subject_code,)).fetchall()

    marks = {row["student_uid"]: dict(row) for row in rows}

    if request.method == "POST":
        credits = db.execute(
            "SELECT credits FROM subjects WHERE subject_code=?",
            (subject_code,)
        ).fetchone()["credits"]

        for stu in students:
            uid = stu["uid"]

            mid1 = request.form.get(f"mid1_{uid}")
            mid2 = request.form.get(f"mid2_{uid}")
            sem  = request.form.get(f"sem_{uid}")

            mid1 = float(mid1) if mid1 else marks.get(uid, {}).get("mid1_marks")
            mid2 = float(mid2) if mid2 else marks.get(uid, {}).get("mid2_marks")
            sem  = float(sem)  if sem  else marks.get(uid, {}).get("sem_marks")

            if mid1 is not None and mid2 is not None and sem is not None:
                total = mid1 + mid2 + sem
                gradepoints = round(total / 10, 1)
                result = "PASS" if total >= 40 else "FAIL"
            else:
                total = gradepoints = result = None

            # ✅ SAVE FIRST
            db.execute("""
                INSERT INTO student_marks
                (student_uid, subject_code, subject_name, credits,
                 mid1_marks, mid2_marks, sem_marks,
                 total_marks, gradepoints, result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_uid, subject_code) DO UPDATE SET
                    mid1_marks = excluded.mid1_marks,
                    mid2_marks = excluded.mid2_marks,
                    sem_marks  = excluded.sem_marks,
                    total_marks = excluded.total_marks,
                    gradepoints = excluded.gradepoints,
                    result = excluded.result
            """, (
                uid, subject_code, subject_name, credits,
                mid1, mid2, sem, total, gradepoints, result
            ))

            # 📧 SEND EMAIL AFTER SAVE
            if (
                result == "FAIL"
                and sem is not None
                and stu["email"]
                and marks.get(uid, {}).get("alert_sent", 0) == 0
            ):
                send_marks_alert(
                    stu["email"],
                    stu["name"],
                    subject_name,
                    total
                )

                db.execute("""
                    UPDATE student_marks
                    SET alert_sent = 1
                    WHERE student_uid=? AND subject_code=?
                """, (uid, subject_code))

        db.commit()
        db.close()
        flash("Marks saved successfully")
        return redirect(url_for("teacher_marks"))

    db.close()
    return render_template(
        "teacher_marks.html",
        students=students,
        marks=marks,
        subject=subject_name
    )


# ---------------- TEACHER VIEW MARKS ----------------
@app.route("/teacher/view_marks")
def teacher_view_marks():
    if "teacher_id" not in session:
        return redirect(url_for("teacher_login"))

    subject_code = session.get("teacher_subject_code")
    subject_name = session.get("teacher_subject_name")

    db = get_db()

    students = db.execute(
        "SELECT uid, name FROM students ORDER BY uid"
    ).fetchall()

    marks_rows = db.execute("""
        SELECT *
        FROM student_marks
        WHERE subject_code = ?
    """, (subject_code,)).fetchall()

    marks = {row["student_uid"]: row for row in marks_rows}

    analytics = calculate_class_analytics(subject_code)

    db.close()

    return render_template(
        "teacher_view_marks.html",
        students=students,
        marks=marks,
        subject_name=subject_name,
        analytics=analytics
    )


# ---------------- CLASS ANALYTICS (SEM-ONLY) ----------------
def calculate_class_analytics(subject_code):
    db = get_db()

    stats = db.execute("""
        SELECT
            COUNT(s.uid) AS total_students,

            COUNT(
                CASE
                    WHEN sm.mid1_marks IS NOT NULL
                     AND sm.mid2_marks IS NOT NULL
                     AND sm.sem_marks  IS NOT NULL
                    THEN 1
                END
            ) AS evaluated_students,

            COUNT(
                CASE
                    WHEN sm.result = 'PASS'
                     AND sm.mid1_marks IS NOT NULL
                     AND sm.mid2_marks IS NOT NULL
                     AND sm.sem_marks  IS NOT NULL
                    THEN 1
                END
            ) AS pass_count,

            COUNT(
                CASE
                    WHEN sm.result = 'FAIL'
                     AND sm.mid1_marks IS NOT NULL
                     AND sm.mid2_marks IS NOT NULL
                     AND sm.sem_marks  IS NOT NULL
                    THEN 1
                END
            ) AS fail_count,

            AVG(
                CASE
                    WHEN sm.mid1_marks IS NOT NULL
                     AND sm.mid2_marks IS NOT NULL
                     AND sm.sem_marks  IS NOT NULL
                    THEN sm.total_marks
                END
            ) AS avg_marks,

            MAX(
                CASE
                    WHEN sm.mid1_marks IS NOT NULL
                     AND sm.mid2_marks IS NOT NULL
                     AND sm.sem_marks  IS NOT NULL
                    THEN sm.total_marks
                END
            ) AS max_marks,

            MIN(
                CASE
                    WHEN sm.mid1_marks IS NOT NULL
                     AND sm.mid2_marks IS NOT NULL
                     AND sm.sem_marks  IS NOT NULL
                    THEN sm.total_marks
                END
            ) AS min_marks

        FROM students s
        LEFT JOIN student_marks sm
            ON s.uid = sm.student_uid
           AND sm.subject_code = ?
    """, (subject_code,)).fetchone()

    grade_dist = db.execute("""
        SELECT
            CASE
                WHEN gradepoints >= 9 THEN 'A'
                WHEN gradepoints >= 8 THEN 'B'
                WHEN gradepoints >= 7 THEN 'C'
                WHEN gradepoints >= 6 THEN 'D'
                ELSE 'F'
            END AS grade,
            COUNT(*) AS count
        FROM student_marks
        WHERE subject_code = ?
          AND mid1_marks IS NOT NULL
          AND mid2_marks IS NOT NULL
          AND sem_marks  IS NOT NULL
        GROUP BY grade
        ORDER BY grade
    """, (subject_code,)).fetchall()

    db.close()

    return {
        "stats": dict(stats),
        "grade_distribution": [dict(r) for r in grade_dist]
    }


# ---------------- STUDENT MARKS PAGE ----------------
@app.route("/student/marks")
def student_marks():
    if "student_id" not in session:
        return redirect(url_for("student_login"))
    return render_template("student_marks.html")


# ---------------- STUDENT MARKS API ----------------
@app.route("/get_student_marks")
def get_student_marks():
    student_uid = session.get("student_uid")
    if not student_uid:
        return jsonify([])

    db = get_db()
    rows = db.execute("""
        SELECT subject_code, subject_name, credits,
               mid1_marks, mid2_marks, sem_marks,
               total_marks, gradepoints, result
        FROM student_marks
        WHERE student_uid = ?
        ORDER BY subject_code
    """, (student_uid,)).fetchall()

    db.close()
    return jsonify([dict(r) for r in rows])



# ---------------- ASSIGNMENT ROUTES ----------------
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import sqlite3, os
from datetime import datetime
from ai_detector import detect_ai


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

def get_db():
    conn = sqlite3.connect("nextgenedu.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- TEACHER CREATE ASSIGNMENT PAGE ----------------
@app.route("/teacher/create_assignment_page")
def create_assignment_page():
    if "teacher_id" not in session:
        return redirect(url_for("teacher_login"))
    return render_template("teacher_create_assignment.html")

# ---------------- TEACHER CREATE ASSIGNMENT POST ----------------
@app.route("/teacher/create_assignment", methods=["POST"])
def create_assignment():
    if "teacher_id" not in session:
        return redirect(url_for("teacher_login"))

    title = request.form.get("title")
    description = request.form.get("description")
    due_date = request.form.get("due_date")
    max_marks = request.form.get("max_marks")
    subject_code = session.get("teacher_subject_code")
    subject_name = session.get("teacher_subject_name")

    db = get_db()
    db.execute(
        "INSERT INTO assignments (subject_code, subject_name, title, description, due_date, max_marks, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (subject_code, subject_name, title, description, due_date, max_marks, datetime.now())
    )
    db.commit()
    flash("Assignment created successfully!")
    return redirect(url_for("teacher_assignments"))
# ---------------- TEACHER VIEW ASSIGNMENTS ----------------
@app.route("/teacher/assignments")
def teacher_assignments():
    if "teacher_id" not in session:
        return redirect(url_for("teacher_login"))

    subject_code = session.get("teacher_subject_code")
    db = get_db()

    try:
        assignments = db.execute(
            "SELECT * FROM assignments WHERE subject_code=? ORDER BY due_date DESC",
            (subject_code,)
        ).fetchall()

        all_students = db.execute(
            "SELECT uid, name FROM students ORDER BY uid"
        ).fetchall()

        assignment_list = []

        for a in assignments:
            processed_submissions = []

            for student in all_students:
                student_uid = student["uid"]
                student_name = student["name"]

                submission = db.execute(
                    "SELECT * FROM student_assignments WHERE assignment_id=? AND student_uid=?",
                    (a["id"], student_uid)
                ).fetchone()

                # Default values
                ai_score = 0
                ai_copied = 0
                relevance_score = 0
                similarity_score = 0
                submission_text = ""

                if submission:
                    # Safe access with dict-like access
                    submission_text = submission["submission_text"] if submission["submission_text"] else ""
                    
                    # 1️⃣ Extract text from PDF if needed
                    if not submission_text and submission["submission_file"]:
                        try:
                            filepath = os.path.join(app.config["UPLOAD_FOLDER"], submission["submission_file"])
                            if os.path.exists(filepath):
                                from pdf_utils import extract_text_from_pdf
                                submission_text = extract_text_from_pdf(filepath)
                                db.execute(
                                    "UPDATE student_assignments SET submission_text=? WHERE id=?",
                                    (submission_text, submission["id"])
                                )
                                db.commit()
                        except Exception as e:
                            print("PDF extraction error:", e)

                    # 2️⃣ AI detection using Lovable
                    try:
                        if submission_text and submission["ai_score"] is None:
                            from ai_detector import detect_ai
                            ai_copied, ai_score = detect_ai(submission_text)
                            db.execute(
                                "UPDATE student_assignments SET ai_score=?, ai_copied=? WHERE id=?",
                                (ai_score, ai_copied, submission["id"])
                            )
                            db.commit()
                        else:
                            ai_score = submission["ai_score"] if submission["ai_score"] is not None else 0
                            ai_copied = submission["ai_copied"] if submission["ai_copied"] is not None else 0
                    except Exception as e:
                        print("AI detection error:", e)

                    # 3️⃣ Relevance score
                    try:
                        relevance_score = submission["relevance_score"] if submission["relevance_score"] is not None else 0
                        if submission_text and a["description"] and relevance_score == 0:
                            from sklearn.feature_extraction.text import TfidfVectorizer
                            from sklearn.metrics.pairwise import cosine_similarity
                            tfidf = TfidfVectorizer().fit([submission_text, a["description"]])
                            sim = cosine_similarity(tfidf.transform([submission_text]),
                                                    tfidf.transform([a["description"]]))[0][0]
                            relevance_score = int(sim * 100)
                            db.execute(
                                "UPDATE student_assignments SET relevance_score=? WHERE id=?",
                                (relevance_score, submission["id"])
                            )
                            db.commit()
                    except Exception as e:
                        print("Relevance error:", e)

                    # 4️⃣ Similarity score
                    try:
                        similarity_score = submission["similarity_score"] if submission["similarity_score"] is not None else 0
                        if submission_text and similarity_score == 0:
                            others = db.execute(
                                "SELECT submission_text FROM student_assignments WHERE assignment_id=? AND student_uid!=? AND submission_text IS NOT NULL",
                                (a["id"], student_uid)
                            ).fetchall()
                            other_texts = [r["submission_text"] for r in others if r["submission_text"]]
                            if other_texts:
                                tfidf = TfidfVectorizer().fit([submission_text] + other_texts)
                                sims = cosine_similarity(tfidf.transform([submission_text]),
                                                         tfidf.transform(other_texts))[0]
                                similarity_score = int(max(sims) * 100)
                                db.execute(
                                    "UPDATE student_assignments SET similarity_score=? WHERE id=?",
                                    (similarity_score, submission["id"])
                                )
                                db.commit()
                    except Exception as e:
                        print("Similarity error:", e)

                # Append processed submission
                processed_submissions.append({
                    "id": submission["id"] if submission else None,
                    "student_uid": student_uid,
                    "student_name": student_name,
                    "submitted": submission["submitted"] if submission else 0,
                    "ai_copied": ai_copied,
                    "ai_score": ai_score,
                    "relevance_score": relevance_score,
                    "similarity_score": similarity_score,
                    "marks": submission["marks"] if submission else None,
                    "feedback": submission["feedback"] if submission else None,
                    "submission_file": submission["submission_file"] if submission else None
                })

            assignment_list.append({
                "id": a["id"],
                "title": a["title"],
                "description": a["description"],
                "due_date": a["due_date"],
                "submissions": processed_submissions
            })

        db.close()
        return render_template("teacher_assignments.html", assignments=assignment_list)

    except Exception as e:
        db.close()
        import traceback
        traceback.print_exc()
        flash("Error loading assignments")
        return redirect(url_for("teacher_dashboard"))
# ---------------- TEACHER SAVE ASSIGNMENT MARKS ----------------
@app.route("/teacher/save_evaluation", methods=["POST"])
def teacher_save_evaluation():
    if "teacher_id" not in session:
        return redirect(url_for("teacher_login"))

    submission_id = request.form.get("submission_id")
    marks = request.form.get("marks")
    feedback = request.form.get("feedback")

    # validate marks
    try:
        marks = int(marks)
    except:
        marks = 0

    if marks < 0:
        marks = 0
    if marks > 25:
        marks = 25

    db = get_db()

    # 🔹 Get submission file before deleting
    submission = db.execute(
        "SELECT submission_file FROM student_assignments WHERE id=?",
        (submission_id,)
    ).fetchone()

    # 🔹 Update marks & feedback
    db.execute("""
        UPDATE student_assignments
        SET marks = ?, feedback = ?
        WHERE id = ?
    """, (marks, feedback, submission_id))

    # 🔹 Delete PDF file from server
    if submission and submission["submission_file"]:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], submission["submission_file"])
        if os.path.exists(filepath):
            os.remove(filepath)

        # 🔹 Remove file reference from DB
        db.execute("""
            UPDATE student_assignments
            SET submission_file = NULL
            WHERE id = ?
        """, (submission_id,))

    db.commit()
    db.close()

    flash("Marks saved and PDF deleted successfully")
    return redirect(url_for("teacher_assignments"))


# ---------------- TEACHER VIEW SINGLE SUBMISSION ----------------
from flask import send_file, flash, redirect, url_for

@app.route("/teacher/view_submission/<int:submission_id>")
def view_submission(submission_id):
    db = get_db()
    submission = db.execute(
        "SELECT * FROM student_assignments WHERE id=?", (submission_id,)
    ).fetchone()
    db.close()

    if not submission:
        flash("Submission not found")
        return redirect(url_for("teacher_assignments"))

    filepath = submission["submission_file"]
    if not filepath:
        flash("No file uploaded")
        return redirect(url_for("teacher_assignments"))

    full_path = os.path.join(app.config["UPLOAD_FOLDER"], filepath)
    if not os.path.exists(full_path):
        flash("File not found on server")
        return redirect(url_for("teacher_assignments"))

    return send_file(full_path, as_attachment=False)




# ---------------- STUDENT VIEW ASSIGNMENTS ----------------
@app.route("/student/assignments/<subject_code>", methods=["GET", "POST"])
def student_assignments(subject_code):
    if "student_uid" not in session:
        return redirect(url_for("student_login"))

    student_uid = session["student_uid"]
    db = get_db()

    # ---------- SUBMIT ASSIGNMENT ----------
    if request.method == "POST":
        assignment_id = request.form.get("assignment_id")
        file = request.files.get("submission_file")
        filename = None
        submission_text = ""

        if file:
            # Save PDF
            filename = f"{student_uid}_{assignment_id}_{file.filename}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Extract text
            from pdf_utils import extract_text_from_pdf
            submission_text = extract_text_from_pdf(filepath)

        # Include manual text if any
        manual_text = request.form.get("submission_text", "")
        if manual_text:
            submission_text += "\n" + manual_text

        # Run AI detection
        # ---------------- AI DETECTION ----------------
        if submission_text:
            ai_copied, ai_score = detect_ai(submission_text)
        else:
            ai_copied, ai_score = 0, 0


        # ---------- Calculate Relevance Score ----------
        assignment = db.execute(
            "SELECT description FROM assignments WHERE id=?",
            (assignment_id,)
        ).fetchone()
        relevance_score = 0
        if assignment and assignment["description"]:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            tfidf = TfidfVectorizer().fit([submission_text, assignment["description"]])
            sim = cosine_similarity(tfidf.transform([submission_text]), tfidf.transform([assignment["description"]]))[0][0]
            relevance_score = int(sim * 100)

        # ---------- Calculate Similarity Score ----------
        # Compare with other students’ submissions for same assignment
        other_submissions = db.execute(
            "SELECT submission_text FROM student_assignments WHERE assignment_id=? AND student_uid!=?",
            (assignment_id, student_uid)
        ).fetchall()
        similarity_score = 0
        if other_submissions:
            tfidf = TfidfVectorizer().fit([submission_text] + [r["submission_text"] for r in other_submissions])
            sims = cosine_similarity(tfidf.transform([submission_text]), tfidf.transform([r["submission_text"] for r in other_submissions]))[0]
            similarity_score = int(max(sims) * 100)  # take highest similarity with any other student

        # Check if submission exists
        existing = db.execute(
            "SELECT * FROM student_assignments WHERE assignment_id=? AND student_uid=?",
            (assignment_id, student_uid)
        ).fetchone()

        if existing:
            db.execute(
                "UPDATE student_assignments SET submitted=1, submission_file=?, ai_score=?, relevance_score=?, similarity_score=?, ai_copied=?, submission_text=?, marks=NULL, feedback=NULL WHERE id=?",
                (filename, ai_score, relevance_score, similarity_score, ai_copied, submission_text, existing["id"])
            )
        else:
            db.execute(
                "INSERT INTO student_assignments (assignment_id, student_uid, submitted, ai_score, relevance_score, similarity_score, ai_copied, submission_file, submission_text) "
                "VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?)",
                (assignment_id, student_uid, ai_score, relevance_score, similarity_score, ai_copied, filename, submission_text)
            )

        db.commit()
        flash("Assignment submitted successfully!")
        return redirect(url_for("student_assignments", subject_code=subject_code))

    # ---------- GET: List assignments ----------
    pending = db.execute(
        "SELECT * FROM assignments WHERE subject_code=? AND id NOT IN "
        "(SELECT assignment_id FROM student_assignments WHERE student_uid=?)",
        (subject_code, student_uid)
    ).fetchall()

    submitted = db.execute(
        "SELECT a.*, sa.* FROM assignments a "
        "JOIN student_assignments sa ON a.id=sa.assignment_id "
        "WHERE sa.student_uid=? AND a.subject_code=?",
        (student_uid, subject_code)
    ).fetchall()

    return render_template("student_assignments.html", pending_assignments=pending, submitted_assignments=submitted)

    
# ---------------- DOWNLOAD UPLOADED FILE ----------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)





# ---------------- STUDENT LOGIN ----------------
@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        uid = request.form["uid"]
        password = request.form["password"]
        db = get_db()
        student = db.execute(
            "SELECT * FROM students WHERE uid=? AND password=?",
            (uid, password)
        ).fetchone()
        db.close()
        if student:
            session["student_id"] = student["id"]
            session["student_uid"] = student["uid"]
            session["student_name"] = student["name"]
            session["student_class"] = student["class"]
            return redirect(url_for("student_dashboard"))
        else:
            flash("Invalid UID or password")
            return redirect(url_for("student_login"))
    return render_template("student_login.html")

# ---------------- STUDENT DASHBOARD ----------------
@app.route("/student/dashboard")
def student_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    student_uid = session['student_uid']

    conn = sqlite3.connect('nextgenedu.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT subject_code, subject_name
        FROM teachers
    """)
    subjects = cur.fetchall()

    subjects_list = []

    for s in subjects:
        # total assignments
        cur.execute("""
            SELECT COUNT(*) AS total_assignments
            FROM assignments
            WHERE subject_code = ?
        """, (s['subject_code'],))
        total = cur.fetchone()['total_assignments'] or 0

        # submitted assignments (✅ FIX)
        cur.execute("""
            SELECT COUNT(*) AS submitted_count
            FROM student_assignments sa
            JOIN assignments a ON sa.assignment_id = a.id
            WHERE sa.student_uid = ?
              AND a.subject_code = ?
              AND sa.submitted = 1
        """, (student_uid, s['subject_code']))
        submitted = cur.fetchone()['submitted_count'] or 0

        pending = total - submitted

        subjects_list.append({
            'subject_code': s['subject_code'],
            'subject_name': s['subject_name'],
            'pending_count': pending
        })

    conn.close()
    return render_template("student_dashboard.html", subjects=subjects_list)



# ---------------- STUDENT SUBJECTS & CHART ----------------
@app.route("/students_subjects")
def students_subject():
    student_id = session.get("student_id")
    if not student_id:
        return redirect(url_for("student_login"))

    subjects = ["Computer Networks", "Python", "Cryptography", "DBMS"]
    db = get_db()
    chart_data = {}

    for sub in subjects:
        rows = db.execute("""
            SELECT score
            FROM quiz_attempts
            WHERE student_id = ? AND subject = ?
            ORDER BY id
        """, (student_id, sub)).fetchall()

        scores = [r["score"] for r in rows]
        attempts = list(range(1, len(scores)+1))

        chart_data[sub] = {
            "attempts": attempts,
            "scores": scores
        }

    db.close()

    return render_template(
        "students_subject.html",
        subjects=subjects,
        chart_data=chart_data
    )

# ---------------- STUDENT SUBJECT PAGES ----------------
@app.route('/computer_networks')
def computer_networks():
    return render_template('computer_networks.html')

@app.route('/python')
def student_python():
    return render_template('python.html')


@app.route('/dbms')
def student_dbms():
    return render_template('dbms.html')

@app.route('/cryptography')
def student_cryptography():
    return render_template('cryptography.html')


# ---------------- FETCH QUIZ QUESTIONS ----------------
@app.route("/get_quiz_questions/<subject>")
def get_quiz_questions(subject):
    db = get_db()
    rows = db.execute("""
        SELECT id, question, option_a, option_b, option_c, option_d, correct_option
        FROM questions
        WHERE subject = ?
        ORDER BY RANDOM()
        LIMIT 5
    """, (subject,)).fetchall()
    db.close()

    questions = []
    for r in rows:
        # Convert options into an array so JS can map over them
        options_array = [r["option_a"], r["option_b"], r["option_c"], r["option_d"]]

        questions.append({
            "id": r["id"],
            "question": r["question"],
            "options": options_array,   # ✅ array
            "answer": r["correct_option"]  # keep track of correct answer
        })

    return jsonify(questions)

# ---------------- SUBMIT QUIZ ----------------
from flask import request, jsonify

@app.route("/submit_quiz/<subject>", methods=["POST"])
def submit_quiz(subject):
    if "student_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    student_id = session["student_id"]
    data = request.get_json()   # parse JSON
    score = int(data.get("score", 0))  # ensure it's a number

    db = get_db()
    db.execute(
        "INSERT INTO quiz_attempts (student_id, subject, score) VALUES (?, ?, ?)",
        (student_id, subject, score)
    )
    db.commit()
    db.close()

    return jsonify({"message": "Score saved", "score": score})


# ---------------- STUDENT TIMETABLE ----------------
@app.route("/student/timetable")
def student_timetable():
    db = get_db()
    timetable = db.execute("""
        SELECT t.day, t.period, s.subject_name AS subject, te.name AS teacher
        FROM timetable t
        JOIN subjects s ON t.subject_code = s.subject_code
        JOIN teachers te ON t.teacher_id = te.id
        ORDER BY 
            CASE t.day
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
            END,
            t.period
    """).fetchall()
    return render_template("student_timetable.html", timetable=timetable)

@app.route("/teacher/timetable")
def teacher_timetable():
    teacher_id = session.get('teacher_id')  # Logged-in teacher
    if not teacher_id:
        return redirect(url_for('login'))  # Redirect if not logged in

    db = get_db()
    timetable = db.execute("""
        SELECT t.day, t.period, s.subject_name AS subject
        FROM timetable t
        JOIN subjects s ON t.subject_code = s.subject_code
        WHERE t.teacher_id = ?
    """, (teacher_id,)).fetchall()

    return render_template("teacher_timetable.html", timetable=timetable)




# ----------------- CHAT ROUTES -----------------
# ---------------- WHATSAPP-STYLE CHAT API ----------------

@app.route("/api/chat/contacts")
def get_chat_contacts():
    """Get list of contacts with last message and unread count"""
    if "teacher_id" in session:
        # Teacher sees all students
        db = get_db()
        students = db.execute("""
            SELECT uid as id, name, 'student' as type
            FROM students
            ORDER BY name
        """).fetchall()
        
        contacts = []
        teacher_id = str(session['teacher_id'])
        
        for student in students:
            # Get last message
            last_msg = db.execute("""
                SELECT message, created_at
                FROM messages
                WHERE (sender_type='teacher' AND sender_id=? AND receiver_type='student' AND receiver_id=?)
                   OR (sender_type='student' AND sender_id=? AND receiver_type='teacher' AND receiver_id=?)
                ORDER BY created_at DESC
                LIMIT 1
            """, (teacher_id, student['id'], student['id'], teacher_id)).fetchone()
            
            # Get unread count
            unread = db.execute("""
                SELECT COUNT(*) as count
                FROM messages
                WHERE sender_type='student' AND sender_id=? 
                  AND receiver_type='teacher' AND receiver_id=?
                  AND is_read=0
            """, (student['id'], teacher_id)).fetchone()
            
            contacts.append({
                'id': student['id'],
                'name': student['name'],
                'type': 'student',
                'last_message': last_msg['message'][:50] + '...' if last_msg else None,
                'last_message_time': last_msg['created_at'] if last_msg else None,
                'unread_count': unread['count']
            })
        
        db.close()
        return jsonify({'contacts': contacts})
        
    elif "student_uid" in session:
        # Student sees all teachers
        db = get_db()
        teachers = db.execute("""
            SELECT id, name, subject_name, 'teacher' as type
            FROM teachers
            ORDER BY name
        """).fetchall()
        
        contacts = []
        student_uid = session['student_uid']
        
        for teacher in teachers:
            teacher_id = str(teacher['id'])
            
            # Get last message
            last_msg = db.execute("""
                SELECT message, created_at
                FROM messages
                WHERE (sender_type='student' AND sender_id=? AND receiver_type='teacher' AND receiver_id=?)
                   OR (sender_type='teacher' AND sender_id=? AND receiver_type='student' AND receiver_id=?)
                ORDER BY created_at DESC
                LIMIT 1
            """, (student_uid, teacher_id, teacher_id, student_uid)).fetchone()
            
            # Get unread count
            unread = db.execute("""
                SELECT COUNT(*) as count
                FROM messages
                WHERE sender_type='teacher' AND sender_id=? 
                  AND receiver_type='student' AND receiver_id=?
                  AND is_read=0
            """, (teacher_id, student_uid)).fetchone()
            
            contacts.append({
                'id': teacher_id,
                'name': f"{teacher['name']} ({teacher['subject_name']})",
                'type': 'teacher',
                'last_message': last_msg['message'][:50] + '...' if last_msg else None,
                'last_message_time': last_msg['created_at'] if last_msg else None,
                'unread_count': unread['count']
            })
        
        db.close()
        return jsonify({'contacts': contacts})
    
    return jsonify({'contacts': []})


@app.route("/api/chat/messages")
def get_chat_messages():
    """Get conversation messages with a specific contact"""
    contact_id = request.args.get('contact_id')
    contact_type = request.args.get('contact_type')
    
    if not contact_id or not contact_type:
        return jsonify({'messages': []})
    
    db = get_db()
    
    if "teacher_id" in session:
        teacher_id = str(session['teacher_id'])
        
        # Get all messages between teacher and student
        messages = db.execute("""
            SELECT 
                message,
                created_at,
                sender_type,
                CASE 
                    WHEN sender_type='teacher' THEN 1 
                    ELSE 0 
                END as is_sent
            FROM messages
            WHERE (sender_type='teacher' AND sender_id=? AND receiver_type='student' AND receiver_id=?)
               OR (sender_type='student' AND sender_id=? AND receiver_type='teacher' AND receiver_id=?)
            ORDER BY created_at ASC
        """, (teacher_id, contact_id, contact_id, teacher_id)).fetchall()
        
    elif "student_uid" in session:
        student_uid = session['student_uid']
        
        # Get all messages between student and teacher
        messages = db.execute("""
            SELECT 
                message,
                created_at,
                sender_type,
                CASE 
                    WHEN sender_type='student' THEN 1 
                    ELSE 0 
                END as is_sent
            FROM messages
            WHERE (sender_type='student' AND sender_id=? AND receiver_type='teacher' AND receiver_id=?)
               OR (sender_type='teacher' AND sender_id=? AND receiver_type='student' AND receiver_id=?)
            ORDER BY created_at ASC
        """, (student_uid, contact_id, contact_id, student_uid)).fetchall()
    else:
        db.close()
        return jsonify({'messages': []})
    
    db.close()
    
    return jsonify({
        'messages': [dict(msg) for msg in messages]
    })


@app.route("/api/chat/send", methods=["POST"])
def send_chat_message():
    """Send a new message"""
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    receiver_type = data.get('receiver_type')
    message = data.get('message', '').strip()
    
    if not receiver_id or not receiver_type or not message:
        return jsonify({'success': False, 'error': 'Missing data'})
    
    # Limit message length
    if len(message) > 5000:
        return jsonify({'success': False, 'error': 'Message too long'})
    
    db = get_db()
    
    try:
        if "teacher_id" in session:
            # Teacher sending to student
            teacher_id = str(session['teacher_id'])
            
            # Get receiver name
            student = db.execute("SELECT name FROM students WHERE uid=?", 
                               (receiver_id,)).fetchone()
            
            if not student:
                db.close()
                return jsonify({'success': False, 'error': 'Student not found'})
            
            db.execute("""
                INSERT INTO messages 
                (sender_type, sender_id, sender_name, receiver_type, 
                 receiver_id, receiver_name, message, subject)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'teacher',
                teacher_id,
                session['teacher_name'],
                'student',
                receiver_id,
                student['name'],
                message,
                None
            ))
            
        elif "student_uid" in session:
            # Student sending to teacher
            student_uid = session['student_uid']
            
            # Get receiver name
            teacher = db.execute("SELECT name FROM teachers WHERE id=?", 
                               (receiver_id,)).fetchone()
            
            if not teacher:
                db.close()
                return jsonify({'success': False, 'error': 'Teacher not found'})
            
            db.execute("""
                INSERT INTO messages 
                (sender_type, sender_id, sender_name, receiver_type, 
                 receiver_id, receiver_name, message, subject)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'student',
                student_uid,
                session['student_name'],
                'teacher',
                receiver_id,
                teacher['name'],
                message,
                None
            ))
        else:
            db.close()
            return jsonify({'success': False, 'error': 'Not authenticated'})
        
        db.commit()
        db.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.close()
        print("Error sending message:", e)
        return jsonify({'success': False, 'error': str(e)})


@app.route("/api/chat/mark_read", methods=["POST"])
def mark_chat_read():
    """Mark messages as read"""
    data = request.get_json()
    contact_id = data.get('contact_id')
    contact_type = data.get('contact_type')
    
    if not contact_id or not contact_type:
        return jsonify({'success': False})
    
    db = get_db()
    
    try:
        if "teacher_id" in session:
            teacher_id = str(session['teacher_id'])
            
            # Mark all messages from this student as read
            db.execute("""
                UPDATE messages
                SET is_read = 1
                WHERE sender_type='student' AND sender_id=?
                  AND receiver_type='teacher' AND receiver_id=?
                  AND is_read=0
            """, (contact_id, teacher_id))
            
        elif "student_uid" in session:
            student_uid = session['student_uid']
            
            # Mark all messages from this teacher as read
            db.execute("""
                UPDATE messages
                SET is_read = 1
                WHERE sender_type='teacher' AND sender_id=?
                  AND receiver_type='student' AND receiver_id=?
                  AND is_read=0
            """, (contact_id, student_uid))
        
        db.commit()
        db.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.close()
        print("Error marking as read:", e)
        return jsonify({'success': False})


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
