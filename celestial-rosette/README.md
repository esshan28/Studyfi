# Smart Curriculum Activity & Attendance App

This project is a complete "Smart Curriculum Activity & Attendance App" designed for the Smart India Hackathon problem statement SIH25011 (Smart Education).

## Features
- **User Authentication**: Secure login for Students and Teachers.
- **QR Attendance**: Teacher generates a QR code, student scans it to mark attendance.
- **Curriculum Management**: Assign tasks, quizzes, and track completion status.
- **Analytics Dashboard**: Visual charts for attendance trends and student performance.
- **Notifications**: Automated alerts for low attendance (<75%) and new tasks.
- **PDF Reports**: Export professional attendance reports in PDF format.
- **Premium UI**: Modern glassmorphism design with responsive Bootstrap 5 layout.

## Tech Stack
- **Backend**: Python, Flask, SQLite
- **Frontend**: HTML5, CSS3, JS, Bootstrap 5
- **Libraries**: Matplotlib, ReportLab, QRCode, Pillow, Werkzeug

## How to Run Locally

1. **Install Dependencies**:
   ```bash
   pip install flask qrcode matplotlib reportlab pillow
   ```

2. **Initialize Database**:
   ```bash
   python init_db.py
   ```

3. **Run the App**:
   ```bash
   python app.py
   ```

4. **Access the App**:
   Open `http://127.0.0.1:5000` in your browser.

### Sample Credentials
- **Teacher**: `teacher@example.com` / `teacher123`
- **Student**: `rahul@example.com` / `student123`

## Project Structure
- `app.py`: Main Flask application with RBAC and feature routes.
- `schema.sql`: Database definition.
- `models/`: Logic for Students, Attendance, Activities, and Notifications.
- `templates/`: HTML templates for all views.
- `static/`: Custom CSS, charts, and QR codes.
