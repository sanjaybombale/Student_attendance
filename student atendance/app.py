from flask import Flask, render_template, request, redirect, session
import psycopg2

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    return psycopg2.connect(
        host="localhost",
        database="student_system",
        user="postgres",
        password="sanjay0303",
        port="5432"
    )

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO users (full_name, email, password)
                VALUES (%s, %s, %s)
            """, (name, email, password))

            conn.commit()
        except Exception as e:
            conn.rollback()
            return str(e)

        cur.close()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, role FROM users
            WHERE email=%s AND password=%s
        """, (email, password))

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session["user"] = user[0]
            session["role"] = user[1]
            return redirect("/dashboard")
        else:
            return "Invalid Login"

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html")

# ---------------- ADD STUDENT ----------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        roll = request.form["roll"]

        conn = get_db()
        cur = conn.cursor()

        try:
            # 1. Insert into users
            cur.execute("""
                INSERT INTO users (full_name, email, password)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (name, email, password))

            user_id = cur.fetchone()[0]

            # 2. Insert into students
            cur.execute("""
                INSERT INTO students (user_id, roll_no)
                VALUES (%s, %s)
            """, (user_id, roll))

            conn.commit()

        except Exception as e:
            conn.rollback()
            return str(e)

        cur.close()
        conn.close()

        return redirect("/students")

    return render_template("add.html")

# ---------------- VIEW STUDENTS ----------------
@app.route("/students")
def students():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.id, u.full_name, u.email, s.roll_no
        FROM students s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.id DESC
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("view.html", students=data)

# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect("/students")

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM courses")
    total_courses = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template("admin.html",
                           total_users=total_users,
                           total_students=total_students,
                           total_courses=total_courses)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)