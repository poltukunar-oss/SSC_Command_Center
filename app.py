from flask import Flask, render_template, request, jsonify, send_file
import sqlite3, shutil, os
from datetime import datetime

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
DB = "ssc_data.db"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS scores(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maths INTEGER, english INTEGER, reasoning INTEGER, gs INTEGER, date TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS errors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT, topic TEXT, description TEXT, image TEXT, date TEXT
    )""")

    conn.commit()
    conn.close()

# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add_score", methods=["POST"])
def add_score():
    data = request.json
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO scores VALUES(NULL,?,?,?,?,?)",
              (data["maths"], data["english"], data["reasoning"], data["gs"],
               datetime.now().strftime("%d-%m-%Y")))
    conn.commit()
    conn.close()
    return jsonify({"ok": 1})

@app.route("/get_scores")
def get_scores():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT maths,english,reasoning,gs,date FROM scores")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

@app.route("/add_error", methods=["POST"])
def add_error():
    subject = request.form["subject"]
    topic = request.form["topic"]
    desc = request.form["description"]
    img_name = ""

    if "image" in request.files:
        img = request.files["image"]
        if img.filename != "":
            img_name = datetime.now().strftime("%H%M%S_") + img.filename
            img.save(os.path.join(app.config["UPLOAD_FOLDER"], img_name))

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO errors VALUES(NULL,?,?,?,?,?)",
              (subject, topic, desc, img_name,
               datetime.now().strftime("%d-%m-%Y")))
    conn.commit()
    conn.close()
    return jsonify({"ok": 1})

@app.route("/get_errors")
def get_errors():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT subject,topic,description,image,date FROM errors ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

@app.route("/backup")
def backup():
    name = f"ssc_backup_{datetime.now().strftime('%Y%m%d')}.db"
    shutil.copy(DB, name)
    return send_file(name, as_attachment=True)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
