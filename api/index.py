from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, db
import os
from datetime import datetime, date

app = Flask(__name__, template_folder='../templates')
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_123")

# --- FIREBASE SETUP ---
if not firebase_admin._apps:
    cred_dict = {
        "type": "service_account",
        "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
        "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    firebase_admin.initialize_app(credentials.Certificate(cred_dict), {
        'databaseURL': os.environ.get("FIREBASE_DATABASE_URL")
    })

def get_data():
    return db.reference("via_master_record").get() or {}

# --- ROUTES ---
@app.route('/')
def home():
    data = get_data()
    members = data.get("members", [])
    logs = data.get("logs", [])
    # Calculate Total Hours
    total_mins = sum(int(l.get('minutes', 0)) for l in logs)
    return render_template('index.html', 
                           members=members, 
                           logs=reversed(logs[-10:]), 
                           total_hours=round(total_mins/60, 1))

@app.route('/log', methods=['POST'])
def log_time():
    name = request.form.get('name')
    task = request.form.get('task')
    mins = request.form.get('minutes')
    
    ref = db.reference("via_master_record/logs")
    ref.push({
        "user": name,
        "task": task,
        "minutes": mins,
        "date": str(date.today()),
        "time": datetime.now().strftime("%H:%M")
    })
    return redirect(url_for('home'))

# Required for Vercel
app = app
