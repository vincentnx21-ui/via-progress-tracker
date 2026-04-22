from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db
import os
from datetime import datetime, date

app = Flask(__name__, template_folder='../templates')

# --- FIREBASE SETUP ---
if not firebase_admin._apps:
    # Set these in Vercel Dashboard -> Settings -> Environment Variables
    cred_dict = {
        "type": "service_account",
        "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
        "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
    }
    firebase_admin.initialize_app(credentials.Certificate(cred_dict), {
        'databaseURL': 'https://via-report-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

def get_data():
    return db.reference("via_master_record").get() or {}

# --- ROUTES ---
@app.route('/')
def dashboard():
    data = get_data()
    logs = data.get("logs", [])
    members = data.get("members", [])
    
    # Calculate Total Minutes (Replaces your Tab 3 logic)
    total_mins = sum(int(l.get('minutes', 0)) for l in logs if isinstance(l, dict))
    
    return render_template('index.html', 
                           total_hours=round(total_mins/60, 1),
                           logs=reversed(logs[-15:]), # Show last 15 logs
                           members=members)

@app.route('/log', methods=['POST'])
def add_log():
    user = request.form.get('user')
    task = request.form.get('task')
    mins = request.form.get('minutes')
    
    if user and task and mins:
        db.reference("via_master_record/logs").push({
            "user": user,
            "task": task,
            "minutes": int(mins),
            "date": str(date.today()),
            "time": datetime.now().strftime("%H:%M")
        })
    return redirect(url_for('dashboard'))

# Required for Vercel deployment
app = app
