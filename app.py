from flask import Flask, render_template, request, redirect, url_for, session
import random
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

import sqlite3

def init_db():
    conn = sqlite3.connect("college.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            phone TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            mark1 INTEGER,
            mark2 INTEGER,
            mark3 INTEGER,
            total INTEGER,
            average REAL
        )
    """)

    conn.commit()
    conn.close()

init_db()

students = []
otp_storage = {}

@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("register"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return "Invalid Credentials"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        phone = request.form.get("phone")

        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password, phone) VALUES (?, ?, ?)",
                (username, password, phone)
            )
            conn.commit()
        except:
            conn.close()
            return "User already exists"

        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        phone = request.form.get("phone")

        for username, data in users.items():
            if data["phone"] == phone:
                otp = str(random.radint(1000, 9999))

                otp_storage[phone] = {
                    "otp": otp,
                    "username": username
                }
                print("OTP for", phone, "is:",otp)
                
                return redirect(url_for("verify_otp"))


        return "Phone number not found"

    return render_template("forgot.html")

@app.route("/verify", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        phone = request.form.get("phone")
        entered_otp = request.form.get("otp")

        if phone in otp_storage and otp_storage[phone]["otp"] == entered_otp:
            session["reset_user"] = otp_storage[phone]["username"]
            return redirect(url_for("reset_password"))

        return "Invalid OTP"

    return render_template("verify.html")


@app.route("/reset", methods=["GET", "POST"])
def reset_password():
    if "reset_user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        new_password = request.form.get("password")
        username = session["reset_user"]

        users[username]["password"] = new_password

        session.pop("reset_user")
        return redirect(url_for("login"))

    return render_template("reset.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/add", methods=["GET", "POST"])
def add_student():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        mark1 = int(request.form["mark1"])
        mark2 = int(request.form["mark2"])
        mark3 = int(request.form["mark3"])

        total = mark1 + mark2 + mark3
        average = round(total / 3, 2)

        student = {
            "name": name,
            "marks": [mark1, mark2, mark3],
            "total": total,
            "average": average
        }

        students.append(student)

        return render_template("students.html", students=students)
       
    return render_template("add.html")

@app.route("/students")
def view_students():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("students.html", students=students)


@app.route("/delete/<int:index>")
def delete_student(index):
    if "user" not in session:
        return redirect(url_for("login"))
    
    if 0 <= index < len(students):
        students.pop(index)
    return render_template("students.html", students=students)

@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit_student(index):
    if "user" not in session:
        return redirect(url_for("login"))

    if 0 <= index < len(students):
        if request.method == "POST":
            name = request.form["name"]
            mark1 = int(request.form["mark1"])
            mark2 = int(request.form["mark2"])
            mark3 = int(request.form["mark3"])

            total = mark1 + mark2 + mark3
            average = round(total / 3, 2)

            students[index] = {
                "name": name,
                "marks": [mark1, mark2, mark3],
                "total": total,
                "average": average
            }

            return render_template("students.html", students=students)

        return render_template("edit.html", student=students[index])

    return "Invalid student"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
