import os
import json
from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__, template_folder='../templates')

# --- INITIALIZE FIREBASE GLOBALLY ---
service_account_info = os.environ.get("FIREBASE_SERVICE_ACCOUNT")

if service_account_info:
    try:
        # Load the JSON string into a dictionary
        info = json.loads(service_account_info)
        
        # Fix the private key formatting
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace('\\n', '\n')
            
        cred = credentials.Certificate(info)
        
        # Check if already initialized to prevent "Duplicate App" errors
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'databaseURL': "https://via-report-default-rtdb.asia-southeast1.firebasedatabase.app/"
            })
    except Exception as e:
        print(f"Firebase Init Error: {e}")
# -------------------------------------

@app.route('/')
def index():
    try:
        # Verify if app was initialized
        if not firebase_admin._apps:
            return "Error: Firebase was not initialized. Check your Environment Variables."
            
        data = db.reference("via_master_record").get() or {}
        members = data.get("members", [])
        return render_template('index.html', members=members)
    except Exception as e:
        # This will catch and show the specific error on your website
        return f"Database Error: {str(e)}"

# Required for Vercel
app = app
