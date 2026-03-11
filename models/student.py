import sqlite3
from werkzeug.security import generate_password_hash

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

class Student:
    @staticmethod
    def get_by_id(student_id):
        conn = get_db()
        student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
        conn.close()
        return student

    @staticmethod
    def get_all_by_teacher(teacher_id):
        conn = get_db()
        students = conn.execute('SELECT * FROM students WHERE teacher_id = ?', (teacher_id,)).fetchall()
        conn.close()
        return students

    @staticmethod
    def get_by_email(email):
        conn = get_db()
        student = conn.execute('SELECT * FROM students WHERE email = ?', (email,)).fetchone()
        conn.close()
        return student

    @staticmethod
    def create(name, roll_number, class_name, email, password, teacher_id):
        conn = get_db()
        hashed_pw = generate_password_hash(password)
        try:
            conn.execute('INSERT INTO students (name, roll_number, class, email, password, teacher_id) VALUES (?, ?, ?, ?, ?, ?)',
                         (name, roll_number, class_name, email, hashed_pw, teacher_id))
            conn.commit()
            success = True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            success = False
        conn.close()
        return success
