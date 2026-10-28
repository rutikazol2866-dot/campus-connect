from flask import Flask, render_template, request, redirect, url_for, flash
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
app.secret_key = "campus-connect-key"
DB_PATH = BASE_DIR / "campusconnect.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            college TEXT NOT NULL,
            course TEXT NOT NULL,
            year TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            salary TEXT NOT NULL,
            description TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            college TEXT NOT NULL,
            course TEXT NOT NULL,
            year TEXT NOT NULL,
            skills TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            venue TEXT NOT NULL,
            description TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            duration TEXT NOT NULL,
            description TEXT NOT NULL
        );
        """)

        if db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0:
            db.executemany("""
                INSERT INTO jobs
                (title, company, location, salary, description)
                VALUES (?, ?, ?, ?, ?)
            """, [
                ("UI/UX Design Intern", "Pixel Studio", "Pune",
                 "₹10,000/month", "Design website screens using Figma."),
                ("Python Developer Intern", "TechNova", "Remote",
                 "₹12,000/month", "Work with Python and Flask."),
                ("Web Developer Intern", "Bright Web", "Pune",
                 "₹8,000/month", "Create responsive websites.")
            ])

        if db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0:
            db.executemany("""
                INSERT INTO events (title, date, venue, description)
                VALUES (?, ?, ?, ?)
            """, [
                ("UI/UX Workshop", "2026-11-10", "Seminar Hall",
                 "Learn Figma and wireframing."),
                ("Campus Coding Day", "2026-11-15", "Computer Lab",
                 "Practice coding with other students.")
            ])

        if db.execute("SELECT COUNT(*) FROM courses").fetchone()[0] == 0:
            db.executemany("""
                INSERT INTO courses (title, duration, description)
                VALUES (?, ?, ?)
            """, [
                ("UI/UX Design", "6 Weeks", "Learn Figma and prototyping."),
                ("Python Programming", "8 Weeks", "Learn Python basics."),
                ("Web Development", "12 Weeks", "Learn HTML, CSS and Flask.")
            ])


@app.route("/")
def home():
    with get_db() as db:
        stats = {
            "students": db.execute(
                "SELECT COUNT(*) FROM students").fetchone()[0],
            "jobs": db.execute(
                "SELECT COUNT(*) FROM jobs").fetchone()[0],
            "events": db.execute(
                "SELECT COUNT(*) FROM events").fetchone()[0],
            "courses": db.execute(
                "SELECT COUNT(*) FROM courses").fetchone()[0],
            "applications": db.execute(
                "SELECT COUNT(*) FROM applications").fetchone()[0]
        }
        jobs = db.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
        events = db.execute("SELECT * FROM events ORDER BY id DESC").fetchall()

    return render_template(
        "index.html", stats=stats, jobs=jobs, events=events
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = [
            request.form.get(key, "").strip()
            for key in ["name", "email", "phone", "college", "course", "year"]
        ]

        if not all(data):
            flash("Please fill all fields.")
            return redirect(url_for("register"))

        with get_db() as db:
            db.execute("""
                INSERT INTO students
                (name, email, phone, college, course, year)
                VALUES (?, ?, ?, ?, ?, ?)
            """, data)

        flash("Student registration successful!")
        return redirect(url_for("students"))

    return render_template("form.html", mode="register")


@app.route("/students")
def students():
    with get_db() as db:
        items = db.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()

    return render_template(
        "list.html", kind="students",
        title="Registered Students", items=items
    )


@app.route("/jobs")
def job_list():
    with get_db() as db:
        items = db.execute(
            "SELECT * FROM jobs ORDER BY id DESC"
        ).fetchall()

    return render_template(
        "list.html", kind="jobs",
        title="Job Opportunities", items=items
    )


@app.route("/apply/<int:job_id>", methods=["POST"])
def apply(job_id):
    keys = ["name", "email", "phone", "college", "course", "year", "skills"]
    data = [request.form.get(key, "").strip() for key in keys]

    if not all(data):
        flash("Please complete all application fields.")
        return redirect(url_for("job_list"))

    with get_db() as db:
        job = db.execute(
            "SELECT id FROM jobs WHERE id = ?", (job_id,)
        ).fetchone()

        if job is None:
            return "Job not found", 404

        db.execute("""
            INSERT INTO applications
            (job_id, name, email, phone, college, course, year, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (job_id, *data))

    flash("Your application has been saved!")
    return redirect(url_for("applications"))


@app.route("/applications")
def applications():
    with get_db() as db:
        items = db.execute("""
            SELECT applications.*, jobs.title AS job_title
            FROM applications
            JOIN jobs ON jobs.id = applications.job_id
            ORDER BY applications.id DESC
        """).fetchall()

    return render_template(
        "list.html", kind="applications",
        title="Job Applications", items=items
    )


@app.route("/events")
def event_list():
    with get_db() as db:
        items = db.execute(
            "SELECT * FROM events ORDER BY id DESC"
        ).fetchall()

    return render_template(
        "list.html", kind="events",
        title="College Events", items=items
    )


@app.route("/courses")
def course_list():
    with get_db() as db:
        items = db.execute(
            "SELECT * FROM courses ORDER BY id DESC"
        ).fetchall()

    return render_template(
        "list.html", kind="courses",
        title="Available Courses", items=items
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
