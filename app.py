
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Connect to database
def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create database table automatically
def create_table():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            usn TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            year TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Home page - display all students
@app.route("/")
def index():
    search = request.args.get("search", "").strip()

    conn = get_db_connection()

    students = conn.execute("""
        SELECT * FROM students
        WHERE name LIKE ? OR usn LIKE ?
        ORDER BY id DESC
    """, (f"%{search}%", f"%{search}%")).fetchall()

    conn.close()

    return render_template("index.html", students=students, search=search)


# Add student
@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"].strip()
        usn = request.form["usn"].strip()
        email = request.form["email"].strip()
        department = request.form["department"].strip()
        year = request.form["year"].strip()

        if not all([name, usn, email, department, year]):
            return "All fields are required.", 400

        conn = get_db_connection()

        try:
            conn.execute("""
                INSERT INTO students
                (name, usn, email, department, year)
                VALUES (?, ?, ?, ?, ?)
            """, (name, usn, email, department, year))

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "This USN already exists. Please use a unique USN.", 400

        conn.close()
        return redirect(url_for("index"))

    return render_template("add_student.html")


# Edit student
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()

    if student is None:
        conn.close()
        return "Student not found.", 404

    if request.method == "POST":
        name = request.form["name"].strip()
        usn = request.form["usn"].strip()
        email = request.form["email"].strip()
        department = request.form["department"].strip()
        year = request.form["year"].strip()

        if not all([name, usn, email, department, year]):
            conn.close()
            return "All fields are required.", 400

        try:
            conn.execute("""
                UPDATE students
                SET name=?, usn=?, email=?, department=?, year=?
                WHERE id=?
            """, (name, usn, email, department, year, id))

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "This USN already exists. Please use a unique USN.", 400

        conn.close()
        return redirect(url_for("index"))

    conn.close()
    return render_template("edit_student.html", student=student)


# Delete student
@app.route("/delete/<int:id>", methods=["POST"])
def delete_student(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    create_table()
    app.run(debug=True)
else:
    create_table()
