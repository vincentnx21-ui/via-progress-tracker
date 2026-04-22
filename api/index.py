from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db
import os
from datetime import datetime, date

app = Flask(__name__, template_folder='../templates')

# --- FIREBASE INITIALIZATION ---
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
        "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
    })
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://via-report-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

def get_data():
    return db.reference("via_master_record").get() or {}

@app.route('/')
def dashboard():
    data = get_data()
    logs = data.get("logs", [])
    members = data.get("members", [])
    
    # Calculate Total Hours (Replacing your Tab 3 logic)
    total_mins = sum(int(l.get('minutes', 0)) for l in logs)
    
    return render_template('index.html', 
                           total_hours=round(total_mins/60, 1),
                           logs=reversed(logs[-10:]),
                           members=members)

@app.route('/submit-log', methods=['POST'])
def submit_log():
    data = {
        "user": request.form.get('user'),
        "task": request.form.get('task'),
        "minutes": int(request.form.get('minutes')),
        "date": str(date.today()),
        "time": datetime.now().strftime("%H:%M")
    }
    db.reference("via_master_record/logs").push(data)
    return redirect(url_for('dashboard'))

app = app # Required for Vercel
