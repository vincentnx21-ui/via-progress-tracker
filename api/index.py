import os
from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db

# Setup Flask to find the templates folder correctly
app = Flask(__name__, template_folder='../templates')

def init_firebase():
    if not firebase_admin._apps:
        # Fetching variables from your Vercel Settings
        private_key = os.environ.get("FIREBASE_PRIVATE_KEY")
        
        # This part handles the hidden "Enter" keys in your Private Key
        if private_key:
            private_key = private_key.replace('\\n', '\n')
            
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
            "private_key": private_key,
            "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
        })
        
        firebase_admin.initialize_app(cred, {
            'databaseURL': os.environ.get("FIREBASE_DATABASE_URL")
        })

@app.route('/')
def index():
    try:
        init_firebase()
        # Fetch data to prove it works
        data = db.reference("via_master_record").get() or {}
        members = data.get("members", [])
        return render_template('index.html', members=members)
    except Exception as e:
        # This will show you the EXACT error on the screen if it fails
        return f"Setup Error: {str(e)}"

# Crucial for Vercel deployment
app = app
