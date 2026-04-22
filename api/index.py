import os
import json
from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__, template_folder='../templates')

# --- GLOBAL INITIALIZATION ---
def connect_to_firebase():
    if not firebase_admin._apps:
        service_account_info = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        if not service_account_info:
            return False
            
        try:
            info = json.loads(service_account_info)
            if "private_key" in info:
                info["private_key"] = info["private_key"].replace('\\n', '\n')
            
            cred = credentials.Certificate(info)
            firebase_admin.initialize_app(cred, {
                'databaseURL': "https://via-report-default-rtdb.asia-southeast1.firebasedatabase.app/"
            })
            return True
        except Exception as e:
            print(f"Init Error: {e}")
            return False
    return True

# Try to connect immediately when the script loads
connect_to_firebase()

@app.route('/')
def index():
    try:
        # Fallback: Try to connect again if the global init failed
        if not connect_to_firebase():
            return "Setup Error: Could not connect to Firebase. Check your Vercel Environment Variables."

        # Fetch data from Realtime Database
        # Note: Ensure 'via_master_record' matches your actual database node name
        data = db.reference("via_master_record").get() or {}
        members = data.get("members", [])
        
        return render_template('index.html', members=members)
    except Exception as e:
        # This will show you exactly why the database call failed
        return f"Database Error: {str(e)}"

# Required for Vercel
app = app
