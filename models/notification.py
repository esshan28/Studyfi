from datetime import datetime
import sqlite3

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

class Notification:
    @staticmethod
    def create(user_id, user_role, message):
        conn = get_db()
        date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute('INSERT INTO notifications (user_id, user_role, message, date_created) VALUES (?, ?, ?, ?)',
                     (user_id, user_role, message, date_created))
        conn.commit()
        conn.close()

    @staticmethod
    def get_for_user(user_id, user_role):
        conn = get_db()
        notes = conn.execute('SELECT * FROM notifications WHERE user_id = ? AND user_role = ? ORDER BY date_created DESC LIMIT 5',
                             (user_id, user_role)).fetchall()
        conn.close()
        return notes

    @staticmethod
    def mark_as_read(note_id):
        conn = get_db()
        conn.execute('UPDATE notifications SET status = "read" WHERE id = ?', (note_id,))
        conn.commit()
        conn.close()
