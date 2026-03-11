from datetime import datetime
import sqlite3

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

class Attendance:
    @staticmethod
    def mark_attendance(student_id, date, status, session_token=None):
        conn = get_db()
        # Check if already marked for today
        existing = conn.execute('SELECT id FROM attendance WHERE student_id = ? AND date = ?', (student_id, date)).fetchone()
        if existing:
            conn.close()
            return False, "Attendance already marked for today."
        
        conn.execute('INSERT INTO attendance (student_id, date, status, session_token) VALUES (?, ?, ?, ?)',
                     (student_id, date, status, session_token))
        conn.commit()
        conn.close()
        return True, "Attendance marked successfully."

    @staticmethod
    def get_student_stats(student_id):
        conn = get_db()
        total = conn.execute('SELECT COUNT(*) FROM attendance WHERE student_id = ?', (student_id,)).fetchone()[0]
        present = conn.execute('SELECT COUNT(*) FROM attendance WHERE student_id = ? AND status = "Present"', (student_id,)).fetchone()[0]
        conn.close()
        percentage = (present / total * 100) if total > 0 else 0
        return {"total": total, "present": present, "percentage": round(percentage, 2)}

    @staticmethod
    def get_class_stats(teacher_id):
        conn = get_db()
        # Join students and attendance to get stats for a teacher's class
        query = '''
            SELECT s.name, s.roll_number, 
                   COUNT(a.id) as total,
                   SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present
            FROM students s
            LEFT JOIN attendance a ON s.id = a.student_id
            WHERE s.teacher_id = ?
            GROUP BY s.id
        '''
        stats = conn.execute(query, (teacher_id,)).fetchall()
        conn.close()
        return stats
