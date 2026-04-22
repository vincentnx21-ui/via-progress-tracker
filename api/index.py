import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__, template_folder='templates')

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

        # ✅ FIXED (use info, NOT env name)
        cred = credentials.Certificate(info)

        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://via-progress-tracker-memory-default-rtdb.asia-southeast1.firebasedatabase.app/"
        })

        print("✅ Firebase initialized")
        return True

    except Exception as e:
        print("🔥 Firebase init error:", e)
        return False


# 🔥 IMPORTANT for Vercel (runs every request)
@app.before_request
def init():
    connect_to_firebase()


# ---------------- LOAD DATA ----------------
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

@app.route('/')
def home():
    try:
        data = load_data()

        total_minutes = sum(l.get("minutes", 0) for l in data["logs"])
        total_hours = total_minutes // 60

        return render_template(
            "index.html",
            members=data["members"],
            logs=data["logs"],
            total_hours=total_hours
        )

    except Exception as e:
        return f"🔥 ERROR: {str(e)}"


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

        key = f"{user}"
        data["contributions"][key] = data["contributions"].get(key, 0) + minutes

        save_data(data)

        return redirect("/")

    except Exception as e:
        return f"🔥 Log Error: {str(e)}"


# ---------------- ADD MEMBER ----------------
@app.route('/add_member', methods=['POST'])
def add_member():
    try:
        data = load_data()

        name = request.form.get("name")

        data["members"].append({
            "name": name
        })

        save_data(data)
        return redirect("/")

    except Exception as e:
        return f"🔥 Member Error: {str(e)}"


# ---------------- API ----------------
@app.route('/api/data')
def api_data():
    return jsonify(load_data())


# Required for Vercel
app = app
