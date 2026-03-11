import sqlite3
from werkzeug.security import generate_password_hash
import os

def init_db():
    db_path = 'database.db'
    # Remove existing db if any for fresh start for StudyFI
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    
    # Add Default Admin
    admin_pass = generate_password_hash('admin123')
    cursor.execute("INSERT INTO admins (name, email, password) VALUES (?, ?, ?)",
                   ('StudyFI Admin', 'admin@studyfi.com', admin_pass))
    admin_id = cursor.lastrowid
    
    # Add Sample Teacher (created by admin)
    teacher_pass = generate_password_hash('teacher123')
    cursor.execute("INSERT INTO teachers (name, email, password, created_by_admin) VALUES (?, ?, ?, ?)",
                   ('Dr. Punjab Singh', 'teacher@example.com', teacher_pass, admin_id))
    teacher_id = cursor.lastrowid
    
    # Add Sample Students (enrolled by teacher)
    student_pass = generate_password_hash('student123')
    students_data = [
        ('S101', 'Rahul Sharma', '10A', 'rahul@example.com', student_pass, teacher_id),
        ('S102', 'Priya Kaur', '10A', 'priya@example.com', student_pass, teacher_id),
        ('S103', 'Amit Verma', '10B', 'amit@example.com', student_pass, teacher_id),
        ('S104', 'Sanya Gupta', '11A', 'sanya@example.com', student_pass, teacher_id),
    ]
    cursor.executemany("INSERT INTO students (roll_number, name, class, email, password, teacher_id) VALUES (?, ?, ?, ?, ?, ?)",
                       students_data)
    
    # Add Sample Activities
    cursor.execute("INSERT INTO activities (title, description, class_name, teacher_id, date_assigned) VALUES (?, ?, ?, ?, ?)",
                   ('Math Assignment 1', 'Solve exercises from Chapter 5.', '10A', teacher_id, '2026-03-01'))
    activity_id = cursor.lastrowid
    
    cursor.execute("SELECT id FROM students")
    for row in cursor.fetchall():
        cursor.execute("INSERT INTO activity_status (activity_id, student_id, status) VALUES (?, ?, ?)",
                       (activity_id, row[0], 'Pending'))

    conn.commit()
    conn.close()
    print("StudyFI Database initialized successfully.")

if __name__ == '__main__':
    init_db()
