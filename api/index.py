import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect
import firebase_admin
from firebase_admin import credentials, db

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '../templates')
)

# ---------------- FIREBASE ----------------
def connect_to_firebase():
    if firebase_admin._apps:
        return True

    try:
        raw = os.environ.get("FIREBASE_SERVICE_ACCOUNT")

        if not raw:
            print("❌ Missing FIREBASE_SERVICE_ACCOUNT")
            return False

        info = json.loads(raw)

        # Fix private key formatting
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace('\\n', '\n')

        cred = credentials.Certificate(info)

        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://via-progress-tracker-memory-default-rtdb.asia-southeast1.firebasedatabase.app/"
        })

        print("✅ Firebase initialized")
        return True

    except Exception as e:
        print("🔥 Firebase init error:", e)
        return False


# Run before every request (important for Vercel)
@app.before_request
def init():
    connect_to_firebase()


# ---------------- DATA ----------------
def load_data():
    try:
        data = db.reference("via_master_record").get() or {}
        data.setdefault("members", [])
        data.setdefault("logs", [])
        data.setdefault("contributions", {})
        return data
    except Exception as e:
        print("🔥 Load error:", e)
        return {
            "members": [],
            "logs": [],
            "contributions": {}
        }


def save_data(data):
    db.reference("via_master_record").set(data)


# ---------------- ROUTES ----------------

# Redirect root → dashboard
@app.route('/')
def home():
    return redirect("/dashboard")


# Dashboard
@app.route('/dashboard')
def dashboard():
    data = load_data()

    logs = data["logs"]
    members = data["members"]

    total_minutes = sum(l.get("minutes", 0) for l in logs)
    total_hours = total_minutes // 60

    return render_template(
        "dashboard.html",
        members=members,
        logs=logs,
        total_hours=total_hours
    )


# Attendance page
@app.route('/attendance')
def attendance():
    data = load_data()

    return render_template(
        "attendance.html",
        members=data["members"],
        contributions=data.get("contributions", {})
    )


# Admin page
@app.route('/admin')
def admin():
    data = load_data()

    return render_template(
        "admin.html",
        members=data["members"]
    )


# ---------------- ADD LOG ----------------
@app.route('/log', methods=['POST'])
def add_log():
    try:
        data = load_data()

        user = request.form.get("user")
        task = request.form.get("task")
        minutes = int(request.form.get("minutes", 0))

        new_log = {
            "user": user,
            "task": task,
            "minutes": minutes,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

        data["logs"].append(new_log)

        # Update contributions
        data["contributions"][user] = data["contributions"].get(user, 0) + minutes

        save_data(data)

        return redirect("/dashboard")

    except Exception as e:
        return f"🔥 Log Error: {str(e)}"


# ---------------- ADD MEMBER ----------------
@app.route('/add_member', methods=['POST'])
def add_member():
    try:
        data = load_data()

        name = request.form.get("name")

        if name:
            data["members"].append({"name": name})

        save_data(data)

        return redirect("/admin")

    except Exception as e:
        return f"🔥 Member Error: {str(e)}"


# ---------------- API ----------------
@app.route('/api/data')
def api_data():
    return jsonify(load_data())


# Required for Vercel
app = app
