from flask import Flask, render_template, request, redirect, session, jsonify, send_file
import sqlite3, os, shutil, uuid, feedparser
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = "ssc_command_center_2026"

DB = "ssc_data.db"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- NEWS SOURCES ----------------

NEWS_SOURCES = {
    "reuters": "https://feeds.reuters.com/reuters/INtopNews",
    "thehindu": "https://www.thehindu.com/news/national/feeder/default.rss",
    "pib": "https://pib.gov.in/rssfeed.aspx"
}

# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cur = conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS scores(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            maths INTEGER, english INTEGER, reasoning INTEGER, gs INTEGER,
            date TEXT
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS errors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT, topic TEXT, description TEXT,
            image TEXT, date TEXT
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS routine(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            time TEXT,
            task TEXT
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS current_affairs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            source TEXT,
            link TEXT,
            date TEXT
        )""")

# ---------------- AUTH GUARD ----------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated

# ---------------- NEWS ENGINE ----------------

def fetch_news(source):
    feed = feedparser.parse(NEWS_SOURCES[source])
    news = []
    for entry in feed.entries[:10]:
        news.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published","")
        })
    return news

def save_daily_news():
    today = datetime.now().strftime("%d-%m-%Y")
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM current_affairs WHERE date=?", (today,))
        if cur.fetchone()[0] > 0:
            return

        for source in NEWS_SOURCES:
            news = fetch_news(source)
            for n in news[:5]:
                cur.execute("""INSERT INTO current_affairs(title,source,link,date)
                               VALUES(?,?,?,?)""",
                            (n["title"], source, n["link"], today))

# ---------------- AUTH ----------------

@app.route("/", methods=["GET","POST"])
def login():
    if "user_id" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        with get_db() as conn:
            user = conn.execute("SELECT id,password FROM users WHERE email=?",
                                (email,)).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            with get_db() as conn:
                conn.execute("INSERT INTO users(email,password) VALUES (?,?)",
                             (email,password))
            return redirect("/")
        except:
            return "User already exists"

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("index.html")

# ---------------- MOCK SCORES ----------------

@app.route("/add_score", methods=["POST"])
@login_required
def add_score():
    data = request.json
    with get_db() as conn:
        conn.execute("""INSERT INTO scores(user_id,maths,english,reasoning,gs,date)
                        VALUES(?,?,?,?,?,?)""",
                     (session["user_id"], data["maths"], data["english"],
                      data["reasoning"], data["gs"],
                      datetime.now().strftime("%d-%m-%Y")))
    return jsonify({"status":"ok"})

@app.route("/get_scores")
@login_required
def get_scores():
    with get_db() as conn:
        rows = conn.execute("""SELECT maths,english,reasoning,gs,date 
                               FROM scores WHERE user_id=?""",
                            (session["user_id"],)).fetchall()
    return jsonify([dict(r) for r in rows])

# ---------------- ERROR BOOK ----------------

@app.route("/add_error", methods=["POST"])
@login_required
def add_error():
    subject = request.form["subject"]
    topic = request.form["topic"]
    desc = request.form["description"]
    file = request.files.get("image")

    filename = ""
    if file and file.filename:
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(UPLOAD_FOLDER, secure_filename(filename)))

    with get_db() as conn:
        conn.execute("""INSERT INTO errors(user_id,subject,topic,description,image,date)
                        VALUES(?,?,?,?,?,?)""",
                     (session["user_id"], subject, topic, desc,
                      filename, datetime.now().strftime("%d-%m-%Y")))
    return redirect("/dashboard")

@app.route("/get_errors")
@login_required
def get_errors():
    with get_db() as conn:
        rows = conn.execute("""SELECT subject,topic,description,image,date 
                               FROM errors WHERE user_id=?""",
                            (session["user_id"],)).fetchall()
    return jsonify([dict(r) for r in rows])

# ---------------- ROUTINE ----------------

@app.route("/save_routine", methods=["POST"])
@login_required
def save_routine():
    data = request.json
    with get_db() as conn:
        conn.execute("DELETE FROM routine WHERE user_id=?", (session["user_id"],))
        for item in data:
            conn.execute("INSERT INTO routine(user_id,time,task) VALUES(?,?,?)",
                         (session["user_id"], item["time"], item["task"]))
    return jsonify({"status":"saved"})

@app.route("/get_routine")
@login_required
def get_routine():
    with get_db() as conn:
        rows = conn.execute("SELECT time,task FROM routine WHERE user_id=?",
                            (session["user_id"],)).fetchall()
    return jsonify([dict(r) for r in rows])

# ---------------- LIVE NEWS ----------------

@app.route("/api/news/<source>")
@login_required
def api_news(source):
    if source not in NEWS_SOURCES:
        return jsonify({"error":"Invalid source"})
    return jsonify(fetch_news(source))

# ---------------- DAILY CURRENT AFFAIRS ----------------

@app.route("/api/current_affairs")
@login_required
def daily_current_affairs():
    today = datetime.now().strftime("%d-%m-%Y")
    with get_db() as conn:
        rows = conn.execute("""SELECT title,source,link 
                               FROM current_affairs WHERE date=?""",
                            (today,)).fetchall()
    return jsonify([dict(r) for r in rows])

# ---------------- BACKUP ----------------

@app.route("/backup")
@login_required
def backup():
    name = f"ssc_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db"
    shutil.copy(DB, name)
    return send_file(name, as_attachment=True)

# ---------------- RUN ----------------

if __name__ == "__main__":
    init_db()
    save_daily_news()
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port, debug=True)
