from flask import Flask, render_template, request, redirect, session, jsonify, send_file
import sqlite3, os, shutil
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "ssc_command_center_2026"

DB = "ssc_data.db"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        maths INTEGER, english INTEGER, reasoning INTEGER, gs INTEGER,
        date TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS errors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        subject TEXT, topic TEXT, description TEXT,
        image TEXT, date TEXT
    )""")

    conn.commit()
    conn.close()

# ---------------- AUTH ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE email=?", (email,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = sqlite3.connect(DB)
            cur = conn.cursor()
            cur.execute("INSERT INTO users (email,password) VALUES (?,?)", (email,password))
            conn.commit()
            conn.close()
            return redirect("/")
        except:
            return "Email already registered"

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    return render_template("index.html")

# ---------------- MOCK SCORE ----------------

@app.route("/add_score", methods=["POST"])
def add_score():
    data = request.json
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO scores (user_id, maths, english, reasoning, gs, date) VALUES (?,?,?,?,?,?)",
        (session["user_id"], data["maths"], data["english"], data["reasoning"], data["gs"], datetime.now().strftime("%d-%m-%Y")))
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"})

@app.route("/get_scores")
def get_scores():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT maths,english,reasoning,gs,date FROM scores WHERE user_id=?", (session["user_id"],))
    rows = cur.fetchall()
    conn.close()
    return jsonify(rows)

# ---------------- ERROR BOOK + IMAGE ----------------

@app.route("/add_error", methods=["POST"])
def add_error():
    subject = request.form["subject"]
    topic = request.form["topic"]
    desc = request.form["description"]
    file = request.files["image"]

    filename = ""
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO errors (user_id,subject,topic,description,image,date) VALUES (?,?,?,?,?,?)",
        (session["user_id"], subject, topic, desc, filename, datetime.now().strftime("%d-%m-%Y")))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/get_errors")
def get_errors():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT subject,topic,description,image,date FROM errors WHERE user_id=?", (session["user_id"],))
    rows = cur.fetchall()
    conn.close()
    return jsonify(rows)

# ---------------- BACKUP ----------------

@app.route("/backup")
def backup():
    name = f"ssc_backup_{datetime.now().strftime('%Y%m%d')}.db"
    shutil.copy(DB, name)
    return send_file(name, as_attachment=True)

# ---------------- RUN ----------------

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
