import sqlite3

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

class Activity:
    @staticmethod
    def create_activity(title, description, teacher_id, date_assigned):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO activities (title, description, teacher_id, date_assigned) VALUES (?, ?, ?, ?)',
                       (title, description, teacher_id, date_assigned))
        activity_id = cursor.lastrowid
        
        # Link to all students assigned to this teacher
        students = conn.execute('SELECT id FROM students WHERE teacher_id = ?', (teacher_id,)).fetchall()
        for s in students:
            conn.execute('INSERT INTO activity_status (activity_id, student_id, status) VALUES (?, ?, ?)',
                         (activity_id, s['id'], 'Pending'))
        
        conn.commit()
        conn.close()
        return activity_id

    @staticmethod
    def get_student_activities(student_id):
        conn = get_db()
        query = '''
            SELECT a.*, ast.status as student_status, ast.submission_date
            FROM activities a
            JOIN activity_status ast ON a.id = ast.activity_id
            WHERE ast.student_id = ?
        '''
        activities = conn.execute(query, (student_id,)).fetchall()
        conn.close()
        return activities

    @staticmethod
    def update_status(activity_id, student_id, status, submission_date=None):
        conn = get_db()
        conn.execute('UPDATE activity_status SET status = ?, submission_date = ? WHERE activity_id = ? AND student_id = ?',
                     (status, submission_date, activity_id, student_id))
        conn.commit()
        conn.close()
