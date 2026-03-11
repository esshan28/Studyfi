import sqlite3
from werkzeug.security import generate_password_hash

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

class Teacher:
    @staticmethod
    def create(name, email, password, admin_id):
        conn = get_db()
        hashed_pw = generate_password_hash(password)
        try:
            conn.execute('INSERT INTO teachers (name, email, password, created_by_admin) VALUES (?, ?, ?, ?)',
                         (name, email, hashed_pw, admin_id))
            conn.commit()
            success = True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            success = False
        conn.close()
        return success

    @staticmethod
    def get_all():
        conn = get_db()
        teachers = conn.execute('SELECT * FROM teachers').fetchall()
        conn.close()
        return teachers

    @staticmethod
    def get_by_id(teacher_id):
        conn = get_db()
        teacher = conn.execute('SELECT * FROM teachers WHERE id = ?', (teacher_id,)).fetchone()
        conn.close()
        return teacher
