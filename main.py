import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from tkinter import Label
import tkinter.font as tkFont
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask import g
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
import sqlite3
import uuid

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"

app.config["DATABASE"] = "datenbank.db"

conn = sqlite3.connect("datenbank.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM assignment_table")
rows = cursor.fetchall()

cursor.close()
conn.close()


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(app.config["DATABASE"])
    return db


@app.teardown_appcontext
def close_db(error):
    db = getattr(g, "_database", None)
    if db is not None:
        db.commit()


@app.route("/")
def index():
    db = get_db()
    cursor = db.execute("SELECT * FROM users ORDER BY work_field")
    rows = cursor.fetchall()
    assign_data = db.execute("SELECT * FROM assignment_table")
    assign_rows = assign_data.fetchall()
    customer_data = db.execute("SELECT * FROM customers")
    customer_rows = customer_data.fetchall()
    project_data = db.execute("SELECT * FROM projects")
    project_rows = project_data.fetchall()
    car_data = db.execute("SELECT * FROM cars")
    car_rows = car_data.fetchall()
    form = LoginForm()
    user_role = request.args.get("user_role", "user")
    return render_template(
        "index.html",
        data=rows,
        assignment_table_data=assign_rows,
        customer_table_data=customer_rows,
        project_table_data=project_rows,
        car_table_data=car_rows,
        form=form,
        user_role=user_role,
    )


# Add a new route for handling login requests
@app.route("/login", methods=["POST"])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

    # Perform authentication logic here, e.g., check credentials against a database
    if username == "admin" and password == "admin":
        return jsonify({"status": "success", "user_role": "admin"})
    else:
        return jsonify({"status": "error", "user_role": "user"})

    return redirect(url_for("index"))


@app.route("/assign_mitarbeiter", methods=["POST"])
def assign_mitarbeiter():
    personal_nr = request.form.get("personal_nr")

    week_id = request.form.get("kw")
    startDate = request.form.get("startDate")
    endDate = request.form.get("endDate")
    year = request.form.get("year")

    project_id = request.form.get("project_id")
    car_id = request.form.get("car_id")
    location = request.form.get("ort")

    extra1 = request.form.get("extra1")
    extra2 = request.form.get("extra2")
    extra3 = request.form.get("extra3")

    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()
    assignment_id = str(uuid.uuid4())

    # Perform database operation to create a new user with the provided inputs
    try:
        cursor.execute(
            "INSERT INTO assignment_table (assignment_id, user_id, car_id, project_id, startDate, endDate, week_id, year, extra1, extra2, extra3, ort) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                assignment_id,
                personal_nr,
                car_id,
                project_id,
                startDate,
                endDate,
                48,
                year,
                extra1,
                extra2,
                extra3,
                location,
            ),
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Mitarbeiter erfolgreich zugewiesen."


@app.route("/submit_m_add", methods=["POST"])
def create_new_user():
    personal_nr = request.form.get("personal_nr")
    vorname = request.form.get("vorname")
    nachname = request.form.get("nachname")
    bereich = request.form.get("bereich")

    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    # Perform database operation to create a new user with the provided inputs
    try:
        cursor.execute(
            "INSERT INTO users (user_id, first_name, last_name, work_field) VALUES (?, ?, ?, ?)",
            (personal_nr, vorname, nachname, bereich),
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Mitarbeiter erfolgreich angelegt."


@app.route("/submit_c_add", methods=["POST"])
def create_new_customer():
    customer_id = request.form.get("customer_id")
    customer_name = request.form.get("customer_name")

    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    # Perform database operation to create a new user with the provided inputs
    try:
        cursor.execute(
            "INSERT INTO customers (customer_id, customer_name) VALUES (?, ?)",
            (customer_id, customer_name),
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Kunde erfolgreich angelegt."


@app.route("/submit_p_add", methods=["POST"])
def create_new_project():
    project_id = request.form.get("project_id")
    project_name = request.form.get("project_name")
    customer_id = request.form.get("customer_id")

    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    # Perform database operation to create a new user with the provided inputs
    try:
        cursor.execute(
            "INSERT INTO projects (project_id, project_name, customer_id) VALUES (?, ?, ?)",
            (project_id, project_name, customer_id),
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Projekt erfolgreich angelegt."


@app.route("/submit_m_delete", methods=["POST"])
def delete_user():
    personal_nr = request.form.get("personal_nr")

    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    # Perform database operation to create a new user with the provided inputs
    try:
        cursor.execute("DELETE FROM users WHERE user_id=?", (personal_nr,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Mitarbeiter erfolgreich entfernt."


class LoginForm(FlaskForm):
    username = StringField("Username", [validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])
    submit = SubmitField("Login")


class CompanyOverviewApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Einsatzplan")
        self.geometry("800x600")
        self.login_frame = LoginFrame(self)
        self.login_frame.pack(fill=tk.BOTH, expand=True)

        self.users = {"admin": "admin", "user": "123"}

    def show_main_frame(self, user_role):
        self.login_frame.destroy()
        self.main_frame = MainFrame(self, user_role)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        form = LoginForm()
        self.main_frame.assign_frame = (
            AssignFrame(self, self.users) if user_role == "admin" else None
        )
        self.main_frame.assign_frame.pack(
            fill=tk.BOTH, expand=True
        ) if self.main_frame.assign_frame else None


class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.username_label = tk.Label(self, text="Username:", font=("Arial", 20))
        self.username_label.pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()
        self.password_label = tk.Label(self, text="Password:", font=("Arial", 20))
        self.password_label.pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()
        self.login_button = tk.Button(
            self, text="Login", command=self.login, font=("Arial", 20)
        )
        self.login_button.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in self.master.users and self.master.users[username] == password:
            self.master.show_main_frame("user")
            return jsonify({"status": "success"})
        elif username == "admin" and password == "admin":
            self.master.show_main_frame("admin")
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error"})


class MainFrame(tk.Frame):
    def __init__(self, master, user_role):
        super().__init__(master)
        self.user_role = user_role
        self.user_assignments = {}  # Store user assignments here

        self.usernames = [
            "Thorsten",
            "Timo B.",
            "Adama",
            "Daniel X.",
            "Albert",
            "Horst",
            "Szymon",
            "Hans-Peter",
            "Igor",
            "Marcel K.",
            "Michael v. H.",
            "Tim",
            "Ray",
            "Matthias G.",
            "Franco M.",
            "Raphael S.",
            "Marc",
            "Frank B.",
            "Jenris P.",
            "Matthias K.",
            "Timo W.",
            "Frank M.",
            "Sabrina M.",
            "Daniel M.",
            "Sinan",
        ]  # Fixed list of users

        # Create the dictionary to store the groups
        self.user_groups = {
            "SCHLOSSER": [
                "Thorsten",
                "Timo B.",
                "Adama",
                "Daniel X.",
                "Albert",
                "Horst",
            ],
            "DREHER & FRÄSER": ["Szymon", "Hans-Peter"],
            "ELEKTRIKER": ["Igor", "Marcel K.", "Michael v. H.", "Tim", "Ray"],
            "FREIER MITARBEITER": ["Matthias G."],
            "BÜRO": [
                "Franco M.",
                "Raphael S.",
                "Marc",
                "Frank B.",
                "Jenris P.",
                "Matthias K.",
                "Timo W.",
                "Frank M.",
                "Sabrina M.",
                "Daniel M.",
            ],
            "HAUSWART": ["Sinan"],
        }

        self.table_frame = TableFrame(self, self.usernames, self.user_groups)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        if self.user_role == "admin":
            self.assign_frame = AssignFrame(self, self.usernames)
            self.assign_frame.pack(fill=tk.BOTH, expand=True)


class TableFrame(tk.Frame):
    def __init__(self, master, usernames, user_groups):
        super().__init__(master)

        self.usernames = usernames
        self.user_groups = user_groups

        """ Passendes Datum zum Wochentag darüber anzeigen """

        self.table = ttk.Treeview(
            self, columns=("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag")
        )
        self.table.heading("#0", text="Name")
        self.table.column("#0", width=100)

        for day in self.table["columns"]:
            self.table.heading(day, text=day)
            self.table.column(day, width=200, minwidth=150)

        # Insert the usernames and group names into the table
        for group, group_usernames in self.user_groups.items():
            parent = ""
            if not self.table.exists(group):
                parent = ""
                self.table.insert(
                    "",
                    "end",
                    text=group,
                    values=[""] * len(self.table["columns"]),
                    open=True,
                )
            else:
                parent = group

            for i, username in enumerate(group_usernames):
                self.table.insert(
                    parent,
                    "end",
                    text=username,
                    values=[""] * len(self.table["columns"]),
                )

        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


class AssignFrame(tk.Frame):
    def __init__(self, master, usernames):
        super().__init__(master)
        self.usernames = usernames
        self.master = master

        self.dropdown_label = tk.Label(self, text="Mitarbeiter:", font=("Arial", 20))
        self.dropdown_label.pack()

        self.dropdown = tk.StringVar(self)
        self.dropdown.set(self.usernames[0])
        self.user_dropdown = tk.OptionMenu(self, self.dropdown, *self.usernames)
        self.user_dropdown.pack()

        self.day_label = tk.Label(self, text="Wochentag:", font=("Arial", 20))
        self.day_label.pack()

        self.day_dropdown = tk.StringVar(self)
        self.day_dropdown.set("Tag wählen")
        self.day_menu = tk.OptionMenu(
            self,
            self.day_dropdown,
            "Montag",
            "Dienstag",
            "Mittwoch",
            "Donnerstag",
            "Freitag",
            "Samstag",
            "Sonntag",
        )
        self.day_menu.pack()

        self.site_label = tk.Label(self, text="Baustelle:", font=("Arial", 20))
        self.site_label.pack()
        self.site_entry = tk.Entry(self)
        self.site_entry.pack()

        self.car_label = tk.Label(self, text="Auto:", font=("Arial", 20))
        self.car_label.pack()

        self.car_dropdown = tk.StringVar(self)
        self.car_dropdown.set("")
        self.car_menu = tk.OptionMenu(
            self,
            self.car_dropdown,
            "",
            "T11 () HB-BE 384",
            "T13 (5/24) HB-SL 344",
            "T14 (4/23) HB-SL 554",
            "T15 (7/23) HB-SL 25",
            "BMW (2/24) HB-SL 133",
        )
        self.car_menu.pack()

        self.assign_button = tk.Button(
            self, text="Zuweisen", command=self.assign, font=("Arial", 20)
        )
        self.assign_button.pack()

    def assign(self):
        selected_user = self.dropdown.get()
        day = self.day_dropdown.get()
        site = self.site_entry.get()
        car = self.car_dropdown.get()

        # Check if the car is already assigned to another user on the same day
        for user, assignments in self.master.user_assignments.items():
            if (
                user != selected_user
                and day in assignments
                and assignments[day].endswith(car)
            ):
                messagebox.showerror(
                    "Assign Error",
                    f"Das Auto {car} ist bereits am {day} von {user} belegt.",
                )
                return

        if selected_user not in self.master.user_assignments:
            self.master.user_assignments[selected_user] = {}

        self.master.user_assignments[selected_user][day] = f"{site}, {car}"

        self.update_table(selected_user)

        messagebox.showinfo("Assign", "Mitarbeiter erfolgreich zugewiesen.")

    def update_table(self, user):
        for day in self.master.user_assignments[user]:
            item_id = None
            for item in self.master.table_frame.table.get_children():
                if self.master.table_frame.table.item(item, "text") == user:
                    item_id = item
                    break

            if item_id is not None:
                self.master.table_frame.table.set(
                    item_id, day, self.master.user_assignments[user][day]
                )


if __name__ == "__main__":
    app.run(debug=True)
