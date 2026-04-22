from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db
import os

app = Flask(__name__, template_folder='../templates')

# Firebase Setup
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
        "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
    })
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.environ.get("FIREBASE_DATABASE_URL")
    })

@app.route('/')
def home():
    # Fetch your data and render the dashboard
    data = db.reference("via_master_record").get() or {}
    return render_template('index.html', data=data)

# Flask needs this to run on Vercel
app = app
