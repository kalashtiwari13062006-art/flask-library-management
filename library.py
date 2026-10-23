from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = "library123"

DATABASE = "library.db"


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Issued books table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS issued_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT NOT NULL,
            book_name TEXT NOT NULL,
            book_number TEXT NOT NULL,
            student_name TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------- LOGIN CHECK ----------------

def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("home.html")


# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        try:

            conn.execute("""
                INSERT INTO users
                (name, username, password)
                VALUES (?, ?, ?)
            """, (name, username, password))

            conn.commit()
            conn.close()

            flash("Account created successfully!", "success")

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            conn.close()

            flash("Username already exists!", "error")

            return redirect(url_for("signup"))

    return render_template("signup.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute("""
            SELECT * FROM users
            WHERE username = ? AND password = ?
        """, (username, password)).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["name"] = user["name"]

            return redirect(url_for("dashboard"))

        else:

            flash("Invalid username or password!", "error")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
@login_required
def dashboard():

    name = session["name"]

    return render_template(
        "dashboard.html",
        name=name
    )


# ---------------- ISSUE BOOK ----------------

@app.route("/issue-book", methods=["GET", "POST"])
@login_required
def issue_book():

    if request.method == "POST":

        book_id = request.form["book_id"]
        book_name = request.form["book_name"]
        book_number = request.form["book_number"]
        student_name = request.form["student_name"]
        issue_date = request.form["issue_date"]
        due_date = request.form["due_date"]

        conn = get_db()

        cursor = conn.execute("""
            INSERT INTO issued_books
            (
                book_id,
                book_name,
                book_number,
                student_name,
                issue_date,
                due_date
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            book_id,
            book_name,
            book_number,
            student_name,
            issue_date,
            due_date
        ))

        conn.commit()

        book = conn.execute("""
            SELECT * FROM issued_books
            WHERE id = ?
        """, (cursor.lastrowid,)).fetchone()

        conn.close()

        return render_template(
            "success.html",
            book=book
        )

    return render_template("issue_book.html")


# ---------------- VIEW BOOKS ----------------

@app.route("/books")
@login_required
def books():

    conn = get_db()

    books = conn.execute("""
        SELECT * FROM issued_books
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "view_book.html",
        books=books
    )


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ---------------- RUN ----------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)