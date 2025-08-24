from flask import Flask, render_template, request, redirect, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions

# ---------------- Database Connection ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # your MySQL password
    database="blood_bank"
)
cursor = db.cursor(dictionary=True)

# ---------------- Home ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- Donors ----------------
@app.route("/add_donor", methods=["GET", "POST"])
def add_donor():
    if "hospital_id" not in session:
        return redirect("/login")
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        blood_group = request.form["blood_group"]
        contact = request.form["contact"]

        cursor.execute(
            "INSERT INTO donors (name, age, blood_group, contact) VALUES (%s, %s, %s, %s)",
            (name, age, blood_group, contact)
        )
        db.commit()
        return redirect("/list_donors")

    return render_template("add_donor.html")


@app.route("/list_donors")
def list_donors():
    cursor.execute("SELECT * FROM donors")
    donors = cursor.fetchall()
    return render_template("list_donors.html", donors=donors)


# ---------------- Patients ----------------
@app.route("/add_patients", methods=["GET", "POST"])
def add_patients():
    if "hospital_id" not in session:
        return redirect("/login")
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        blood_group = request.form["blood_group"]
        contact = request.form["contact"]

        cursor.execute(
            "INSERT INTO patients (name, age, blood_group, contact) VALUES (%s, %s, %s, %s)",
            (name, age, blood_group, contact)
        )
        db.commit()
        return redirect("/list_patients")

    return render_template("add_patients.html")


@app.route("/list_patients")
def list_patients():
    if "hospital_id" not in session:
        return redirect("/login")
    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    return render_template("list_patients.html", patients=patients)


# ---------------- Search Donor ----------------
@app.route("/search_donor", methods=["GET", "POST"])
def search_donor():
    donors = []
    if request.method == "POST":
        blood_group = request.form["blood_group"]
        cursor.execute("SELECT * FROM donors WHERE blood_group=%s", (blood_group,))
        donors = cursor.fetchall()
    return render_template("search_donor.html", donors=donors)


# ---------------- Hospital Authentication ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO hospitals (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        db.commit()
        return redirect("/login")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM hospitals WHERE email=%s", (email,))
        hospital = cursor.fetchone()

        if hospital and check_password_hash(hospital["password"], password):
            session["hospital_id"] = hospital["id"]
            session["hospital_name"] = hospital["name"]
            return redirect("/")
        else:
            return "Invalid email or password", 401
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- Donations ----------------
@app.route("/add_donation", methods=["GET", "POST"])
def add_donation():
    if "hospital_id" not in session:
        return redirect("/login")
    if request.method == "POST":
        donor_id = request.form["donor_id"]
        patient_id = request.form["patient_id"]
        donation_date = request.form["donation_date"]

        cursor.execute(
            "INSERT INTO donations (donor_id, patient_id, donation_date) VALUES (%s, %s, %s)",
            (donor_id, patient_id, donation_date)
        )
        db.commit()
        return redirect("/donation_history")

    # Fetch donors and patients for dropdowns
    cursor.execute("SELECT id, name FROM donors")
    donors = cursor.fetchall()
    cursor.execute("SELECT id, name FROM patients")
    patients = cursor.fetchall()

    return render_template("add_donation.html", donors=donors, patients=patients)


@app.route("/donation_history")
def donation_history():
    if "hospital_id" not in session:
        return redirect("/login")

    query = """
        SELECT dn.id, d.name AS donor_name, p.name AS patient_name, dn.donation_date
        FROM donations dn
        JOIN donors d ON dn.donor_id = d.id
        JOIN patients p ON dn.patient_id = p.id
        ORDER BY dn.donation_date DESC
    """
    cursor.execute(query)
    donations = cursor.fetchall()
    return render_template("donation_history.html", donations=donations)


if __name__ == "__main__":
    app.run(debug=True)






