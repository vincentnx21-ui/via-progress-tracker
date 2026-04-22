import os
import json
from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__, template_folder='../templates')

def init_firebase():
    if not firebase_admin._apps:
        # Get the entire JSON string from Vercel
        service_account_info = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        
        if service_account_info:
            # Parse the string into a real dictionary
            info = json.loads(service_account_info)
            
            # Handle the private key line breaks
            if "private_key" in info:
                info["private_key"] = info["private_key"].replace('\\n', '\n')
            
            cred = credentials.Certificate(info)
            firebase_admin.initialize_app(cred, {
                'databaseURL': "https://via-report-default-rtdb.asia-southeast1.firebasedatabase.app/"
            })

@app.route('/')
def index():
    try:
        init_firebase()
        data = db.reference("via_master_record").get() or {}
        members = data.get("members", [])
        return render_template('index.html', members=members)
    except Exception as e:
        return f"Database Error: {str(e)}"

app = app
