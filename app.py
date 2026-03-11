from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import os
import qrcode
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import uuid

# Import models
from models.student import Student
from models.teacher import Teacher
from models.attendance import Attendance
from models.activity import Activity

app = Flask(__name__)
app.secret_key = 'studyfi_premium_sih_2025'
app.config['DATABASE'] = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# --- Authentication Helpers ---
def login_required(role=None):
    def wrapper(f):
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Login required.", "danger")
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash(f"Access denied. Require {role} role.", "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return wrapper

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for(f"{session['role']}_dashboard"))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        # Search across 3 tables
        user = conn.execute('SELECT *, "admin" as role FROM admins WHERE email = ?', (email,)).fetchone()
        if not user:
            user = conn.execute('SELECT *, "teacher" as role FROM teachers WHERE email = ?', (email,)).fetchone()
        if not user:
            user = conn.execute('SELECT *, "student" as role FROM students WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for(f"{user['role']}_dashboard"))
        else:
            flash("Invalid email or password.", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Successfully logged out.", "info")
    return redirect(url_for('login'))

# --- Admin Dashboard ---

@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    teachers = Teacher.get_all()
    conn = get_db_connection()
    students_count = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    teachers_count = len(teachers)
    conn.close()
    return render_template('admin_dashboard.html', teachers=teachers, students_count=students_count, teachers_count=teachers_count)

@app.route('/admin/add_teacher', methods=['POST'])
@login_required('admin')
def add_teacher():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    admin_id = session['user_id']
    
    if Teacher.create(name, email, password, admin_id):
        flash(f"Teacher {name} added successfully.", "success")
    else:
        flash("Failed to add teacher.", "danger")
    return redirect(url_for('admin_dashboard'))

# --- Teacher Dashboard ---

@app.route('/teacher/dashboard')
@login_required('teacher')
def teacher_dashboard():
    teacher_id = session['user_id']
    students = Student.get_all_by_teacher(teacher_id)
    return render_template('teacher_dashboard.html', students=students)

@app.route('/teacher/enroll_student', methods=['POST'])
@login_required('teacher')
def enroll_student():
    name = request.form['name']
    roll_number = request.form['roll_number']
    class_name = request.form['class']
    email = request.form['email']
    password = request.form['password']
    teacher_id = session['user_id']
    
    if Student.create(name, roll_number, class_name, email, password, teacher_id):
        flash(f"Student {name} enrolled.", "success")
    else:
        flash("Enrollment failed. Email or Roll No already exists.", "danger")
    return redirect(url_for('teacher_dashboard'))

# --- Student Dashboard ---

@app.route('/student/dashboard')
@login_required('student')
def student_dashboard():
    student_id = session['user_id']
    stats = Attendance.get_student_stats(student_id)
    activities = Activity.get_student_activities(student_id)
    return render_template('student_dashboard.html', stats=stats, activities=activities)

# --- QR & Attendance API ---

import csv
from flask import Response

# --- QR & Attendance Extensions ---

@app.route('/api/generate_qr', methods=['POST'])
@login_required()
def generate_qr():
    if session['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403
        
    class_name = request.json.get('class_name')
    if not class_name:
        return jsonify({"error": "Class name required"}), 400

    token = str(uuid.uuid4())
    img = qrcode.make(token)
    
    qr_path = f'static/qrcodes/qr_{token}.png'
    os.makedirs('static/qrcodes', exist_ok=True)
    img.save(qr_path)
    
    return jsonify({"qr_url": url_for('static', filename=f'qrcodes/qr_{token}.png'), "token": token})

@app.route('/api/mark_attendance', methods=['POST'])
@login_required('student')
def api_mark_attendance():
    token = request.json.get('token')
    student_id = session['user_id']
    date = datetime.now().strftime('%Y-%m-%d')
    
    # Get student's class
    student = Student.get_by_id(student_id)
    class_name = student['class']
    
    # Use the static method with class_name
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO attendance (student_id, class_name, date, status, session_token) VALUES (?, ?, ?, ?, ?)',
                     (student_id, class_name, date, 'Present', token))
        conn.commit()
        success, msg = True, "Attendance marked successfully."
    except sqlite3.IntegrityError:
        success, msg = False, "Attendance already marked for today."
    finally:
        conn.close()
        
    return jsonify({"success": success, "message": msg})

# --- Activity Management ---

@app.route('/teacher/assign_activity', methods=['POST'])
@login_required('teacher')
def assign_activity():
    title = request.form['title']
    description = request.form['description']
    class_name = request.form['class_name']
    teacher_id = session['user_id']
    date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO activities (title, description, class_name, teacher_id, date_assigned) VALUES (?, ?, ?, ?, ?)',
                   (title, description, class_name, teacher_id, date))
    activity_id = cursor.lastrowid
    
    # Assign to all students in that class
    students = conn.execute('SELECT id FROM students WHERE class = ?', (class_name,)).fetchall()
    for student in students:
        conn.execute('INSERT INTO activity_status (activity_id, student_id, status) VALUES (?, ?, ?)',
                     (activity_id, student['id'], 'Pending'))
    
    conn.commit()
    conn.close()
    flash(f"Activity assigned to class {class_name}.", "success")
    return redirect(url_for('teacher_dashboard'))

@app.route('/api/toggle_activity', methods=['POST'])
@login_required('student')
def toggle_activity():
    activity_id = request.json.get('activity_id')
    student_id = session['user_id']
    
    conn = get_db_connection()
    current = conn.execute('SELECT status FROM activity_status WHERE activity_id = ? AND student_id = ?', 
                           (activity_id, student_id)).fetchone()
    if current:
        new_status = 'Completed' if current['status'] == 'Pending' else 'Pending'
        date = datetime.now().strftime('%Y-%m-%d') if new_status == 'Completed' else None
        conn.execute('UPDATE activity_status SET status = ?, submission_date = ? WHERE activity_id = ? AND student_id = ?',
                     (new_status, date, activity_id, student_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "new_status": new_status})
    conn.close()
    return jsonify({"success": False})

# --- Reporting & CSV ---

@app.route('/export_attendance/<class_name>')
@login_required()
def export_attendance(class_name):
    if session['role'] not in ['admin', 'teacher']:
        return redirect(url_for('index'))
        
    conn = get_db_connection()
    query = '''
        SELECT s.name, s.roll_number, a.class_name, a.date, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.class_name = ?
        ORDER BY a.date DESC
    '''
    records = conn.execute(query, (class_name,)).fetchall()
    conn.close()

    def generate():
        data = [['Student Name', 'Roll Number', 'Class', 'Date', 'Status']]
        for r in records:
            data.append([r['name'], r['roll_number'], r['class_name'], r['date'], r['status']])
        
        output = BytesIO()
        writer = csv.writer(Response().stream) # Dummy for generator pattern
        # Easier way for small files:
        import io
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerows(data)
        return si.getvalue()

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=attendance_{class_name}.csv"}
    )

@app.route('/admin/reports')
@login_required('admin')
def admin_reports():
    conn = get_db_connection()
    teacher_count = conn.execute('SELECT COUNT(*) FROM teachers').fetchone()[0]
    student_count = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    
    # Class-wise stats for Chart.js
    class_stats = conn.execute('''
        SELECT class_name, 
               COUNT(*) as total_records,
               SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present_count
        FROM attendance
        GROUP BY class_name
    ''').fetchall()
    
    classes = [r['class_name'] for r in class_stats]
    percentages = [(r['present_count']/r['total_records'])*100 if r['total_records'] > 0 else 0 for r in class_stats]
    
    conn.close()
    return render_template('reports.html', 
                           teacher_count=teacher_count, 
                           student_count=student_count,
                           chart_labels=classes,
                           chart_data=percentages)

# --- Student Profile (Teacher/Admin view) ---

@app.route('/student/profile/<int:student_id>')
@login_required()
def view_profile(student_id):
    if session['role'] == 'student' and session['user_id'] != student_id:
        return redirect(url_for('index'))
        
    student = Student.get_by_id(student_id)
    stats = Attendance.get_student_stats(student_id)
    activities = Activity.get_student_activities(student_id)
    
    conn = get_db_connection()
    history = conn.execute('SELECT * FROM attendance WHERE student_id = ? ORDER BY date DESC', (student_id,)).fetchall()
    conn.close()
    
    return render_template('profile.html', student=student, stats=stats, activities=activities, history=history)

if __name__ == '__main__':
    app.run(debug=True)
