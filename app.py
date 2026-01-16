from flask import Flask, render_template, request, redirect, session, jsonify, send_file
import sqlite3, os, shutil, uuid, feedparser
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

# ===== GEMINI =====
import google.generativeai as genai
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
# Provide your API key via the GENAI_API_KEY environment variable or a .env file
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
app.secret_key = "ssc_command_center_2026"

DB = "ssc_data.db"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

NEWS_SOURCES = {
    "reuters": "https://feeds.reuters.com/reuters/INtopNews",
    "thehindu": "https://www.thehindu.com/news/national/feeder/default.rss",
    "pib": "https://pib.gov.in/rssfeed.aspx"
}

# ---------------- DB ----------------
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,email TEXT UNIQUE,password TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS scores(id INTEGER PRIMARY KEY,user_id INTEGER,maths INTEGER,english INTEGER,reasoning INTEGER,gs INTEGER,date TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS errors(id INTEGER PRIMARY KEY,user_id INTEGER,subject TEXT,topic TEXT,description TEXT,image TEXT,date TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS routine(id INTEGER PRIMARY KEY,user_id INTEGER,time TEXT,task TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS current_affairs(id INTEGER PRIMARY KEY,title TEXT,source TEXT,link TEXT,date TEXT)""")

# ---------------- AUTH ----------------
def login_required(f):
    @wraps(f)
    def wrap(*a,**k):
        if "user_id" not in session: return redirect("/")
        return f(*a,**k)
    return wrap

@app.route("/",methods=["GET","POST"])
def login():
    if "user_id" in session: return redirect("/dashboard")
    if request.method=="POST":
        with get_db() as conn:
            u = conn.execute("SELECT id,password FROM users WHERE email=?",(request.form["email"],)).fetchone()
        if u and check_password_hash(u["password"], request.form["password"]):
            session["user_id"]=u["id"]; return redirect("/dashboard")
    return render_template("login.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        try:
            with get_db() as conn:
                conn.execute("INSERT INTO users(email,password) VALUES (?,?)",
                             (request.form["email"], generate_password_hash(request.form["password"])))
            return redirect("/")
        except: return "User already exists"
    return render_template("register.html")

@app.route("/logout")
def logout(): session.clear(); return redirect("/")

@app.route("/dashboard")
@login_required
def dashboard(): return render_template("index.html")

# ---------------- NEWS ----------------
def fetch_news(source):
    feed = feedparser.parse(NEWS_SOURCES[source])
    return [{"title":e.title,"link":e.link} for e in feed.entries[:10]]

def save_daily_news():
    today=datetime.now().strftime("%d-%m-%Y")
    with get_db() as conn:
        if conn.execute("SELECT COUNT(*) FROM current_affairs WHERE date=?",(today,)).fetchone()[0]>0: return
        for s in NEWS_SOURCES:
            for n in fetch_news(s)[:5]:
                conn.execute("INSERT INTO current_affairs(title,source,link,date) VALUES(?,?,?,?)",
                             (n["title"],s,n["link"],today))

@app.route("/api/news/<source>")
@login_required
def api_news(source): return jsonify(fetch_news(source))

@app.route("/api/current_affairs")
@login_required
def api_ca():
    today=datetime.now().strftime("%d-%m-%Y")
    with get_db() as conn:
        rows=conn.execute("SELECT title,source,link FROM current_affairs WHERE date=?",(today,)).fetchall()
    return jsonify([dict(r) for r in rows])

# ---------------- GEMINI FACT ----------------
@app.route("/api/daily_fact")
@login_required
def daily_fact():
    prompt = """Give ONE very short, exam-oriented SSC fact.
Focus on BNS, Indian culture, constitution, history or static GK.
Format:
Title: ...
Fact: ...
(2-3 lines only)"""
    try:
        r = model.generate_content(prompt)
        return jsonify({"fact": r.text.strip()})
    except:
        return jsonify({"fact":"Unable to load fact"})

# ---------------- RUN ----------------
if __name__=="__main__":
    init_db(); save_daily_news()
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=True)
