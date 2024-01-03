import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from tkinter import Label
import tkinter.font as tkFont
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask import g
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
import sqlite3
import uuid
import json
from datetime import datetime, timedelta
import locale
import math
import holidays

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


def get_current_week_number():
    today_date = datetime.now()
    return today_date.isocalendar()[
        1
    ]  # Extract the week number from the isocalendar tuple


def generate_week_dates(start_date):
    week_dates = [start_date + timedelta(days=i) for i in range(7)]
    return [date.strftime("%Y-%m-%d") for date in week_dates]


def generate_week_days(start_date):
    locale.setlocale(locale.LC_TIME, "de_DE")
    week_days = [start_date + timedelta(days=i) for i in range(7)]
    return [date.strftime("%a") for date in week_days]


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

    current_week_number = get_current_week_number()
    week_number1 = int(request.args.get("week_number1", 0))  # only for the assignments
    week_number2 = int(request.args.get("week_number2", 1))
    today_date = datetime.now()

    # to show the right KW
    kw_1 = int(request.args.get("kw_1", today_date.isocalendar()[1]))

    iso_year = today_date.isocalendar()[0]
    iso_week = kw_1

    if iso_week == 53:
        iso_week = 1
        iso_year += 1

    if iso_week == 0:
        iso_week = 52
        iso_year -= 1

    kw_2 = int(request.args.get("kw_2", iso_week + 1))

    if kw_2 == 53:
        kw_2 = 1
        iso_year += 1

    if kw_2 == 0:
        kw_2 = 52
        iso_year -= 1

    start_date1 = (
        today_date
        - timedelta(days=today_date.weekday())
        + timedelta(weeks=week_number1)
    )
    end_date1 = start_date1 + timedelta(days=6)

    start_date2 = (
        today_date
        - timedelta(days=today_date.weekday())
        + timedelta(weeks=week_number2)
    )
    end_date2 = start_date2 + timedelta(days=6)

    week_dates1 = generate_week_dates(start_date1)
    week_dates2 = generate_week_dates(start_date2)

    week_days1 = generate_week_days(start_date1)
    week_days2 = generate_week_days(start_date2)

    n_holidays = holidays.country_holidays(
        "DE", subdiv="HB", language="en_US", years=2024
    )  # Feiertage in Bremen
    s_holidays = holidays.country_holidays(
        "DE", subdiv="BY", language="en_US", years=2024
    )  # Bayern, da es die meisten Feiertage hat

    return render_template(
        "index.html",
        data=rows,
        assignment_table_data=assign_rows,
        customer_table_data=customer_rows,
        project_table_data=project_rows,
        car_table_data=car_rows,
        form=form,
        user_role=user_role,
        current_week_number=current_week_number,
        kw_1=iso_week,
        kw_2=kw_2,
        week_number1=week_number1,
        week_number2=week_number2,
        start_date1=start_date1.strftime("%Y-%m-%d"),
        end_date1=end_date1.strftime("%Y-%m-%d"),
        start_date2=start_date2.strftime("%Y-%m-%d"),
        end_date2=end_date2.strftime("%Y-%m-%d"),
        week_dates1=week_dates1,
        week_dates2=week_dates2,
        week_days1=week_days1,
        week_days2=week_days2,
        n_holidays=n_holidays,
        s_holidays=s_holidays,
    )


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

    startDate = request.form.get("startDate")
    endDate = request.form.get("endDate")
    year = request.form.get("year")
    location = request.form.get("ort")

    project_id = request.form.get("project_id", 0)

    if project_id == "null":
        project_id = 0

    car_id = request.form.get("car_id")

    if car_id == "null":
        car_id = 99

    extra1 = request.form.get("extra1")

    if extra1 == "null":
        extra1 = "no"

    extra2 = request.form.get("extra2")

    if extra2 == "null":
        extra2 = "no"

    extra3 = request.form.get("extra3")

    if extra3 == "null":
        extra3 = "no"

    hinweis = request.form.get("hinweis", "")

    abw = request.form.get("checkedRadioButton")

    print(
        f"Received values: personal_nr={personal_nr}, startDate={startDate}, endDate={endDate}, year={year}, project_id={project_id}, car_id={car_id},extra={extra1, extra2, extra3}, checkboxValue={abw}"
    )

    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    try:
        # Check if the user already has an entry between the startDate and endDate
        cursor.execute(
            "SELECT COUNT(*) FROM assignment_table WHERE user_id = ? AND startDate <= ? AND endDate >= ?",
            (personal_nr, endDate, startDate),
        )
        count = cursor.fetchone()[0]

        if count > 0:
            return "Der Mitarbeiter hat schon eine Zuteilung zwischen dem ausgewählten Datum."

        # Check if the assignment already exists
        cursor.execute(
            "SELECT COUNT(*) FROM assignment_table WHERE user_id = ? AND startDate = ? AND endDate = ?",
            (personal_nr, startDate, endDate),
        )
        count = cursor.fetchone()[0]

        if count > 0:
            return "Die Zuteilung existiert bereits."

        if car_id != 99:
            cursor.execute(
                "SELECT COUNT(*) FROM assignment_table WHERE car_id = ? AND startDate <= ? AND endDate >= ?",
                (car_id, endDate, startDate),
            )

            car_cnt = cursor.fetchone()[0]

            if car_cnt > 0:
                return "Auto ist bereits zugewiesen."

        # Insert the assignment into the database
        cursor.execute(
            "INSERT INTO assignment_table (user_id, car_id, project_id, startDate, endDate, year, extra1, extra2, extra3, ort, group_id, hinweis, abwesend) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                personal_nr,
                car_id,
                project_id,
                startDate,
                endDate,
                year,
                extra1,
                extra2,
                extra3,
                location,
                0,  # Weil nur ein einzelner Mitarbeiter hinzugefügt wird und er keine Gruppe hat
                hinweis,
                abw,
            ),
        )
        conn.commit()

        return "Mitarbeiter erfolgreich zugewiesen."
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return "An error occurred while assigning the employee."
    finally:
        conn.close()


@app.route("/get_assignment_hinweis", methods=["POST"])
def get_assignment_hinweis():
    assignment_id = request.form.get("assignmentId")

    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT hinweis FROM assignment_table WHERE assignment_id=?", (assignment_id,)
    )
    result = cursor.fetchone()

    if result:
        hinweis = result[0]
    else:
        hinweis = ""

    return jsonify({"hinweis": hinweis})


@app.route("/assign_group", methods=["POST"])
def assign_group():
    # Use getlist to retrieve a list of values for the "personal_nr_list" key
    personal_nr_list = request.form.getlist("personal_nr_list")

    # Convert user IDs to integers
    numeric_user_ids = [
        int(user_id) for user_id in ",".join(personal_nr_list).split(",")
    ]

    print("Numeric User IDs before list:", numeric_user_ids)

    startDate = request.form.get("startDate")
    endDate = request.form.get("endDate")
    year = request.form.get("year")
    location = request.form.get("ort")
    extra1 = request.form.get("extra1")
    extra2 = request.form.get("extra2")
    extra3 = request.form.get("extra3")
    hinweis = request.form.get("hinweis")
    project_id = request.form.get("project_id")
    car_id = request.form.get("car_id")

    if car_id == "null":
        car_id = 99

    if extra1 == "null":
        extra1 = "no"

    if extra2 == "null":
        extra2 = "no"

    if extra3 == "null":
        extra3 = "no"

    abw = 0

    # Get the highest group_id from the database
    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT MAX(group_id) FROM assignment_table")
        max_group_id = cursor.fetchone()[0]
        if max_group_id is None:
            max_group_id = 0  # If there are no existing group_ids, start from 0

        # Increment the highest group_id for the next assignment
        next_group_id = max_group_id + 1
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        next_group_id = (
            None  # Handle the case where there's an error getting the group_id
        )
    finally:
        conn.close()

    if next_group_id is not None:
        # Remove duplicate user IDs
        numeric_user_ids = list(set(numeric_user_ids))

        # Insert assignments for each user in numeric_user_ids
        conn = sqlite3.connect("datenbank.db")
        cursor = conn.cursor()

        print(f"Received values: startDate={startDate}, endDate={endDate}, year={year}")

        try:
            print("Numeric User IDs after list:", numeric_user_ids)
            print("Next Group ID:", next_group_id)

            if car_id != 99:
                cursor.execute(
                    "SELECT COUNT(*) FROM assignment_table WHERE car_id = ? AND startDate <= ? AND endDate >= ? AND group_id != ?",
                    (car_id, endDate, startDate, next_group_id),
                )

                car_cnt = cursor.fetchone()[0]

                if car_cnt > 0:
                    return "Auto ist bereits in anderer Gruppe zugewiesen."

            for user_id in numeric_user_ids:
                cursor.execute(
                    "SELECT COUNT(*) FROM assignment_table WHERE user_id = ? AND startDate <= ? AND endDate >= ?",
                    (user_id, endDate, startDate),
                )
                count = cursor.fetchone()[0]

                if count > 0:
                    return (
                        "Der Mitarbeiter "
                        + f"{user_id}"
                        + " hat schon eine Zuteilung zwischen dem ausgewählten Datum."
                    )

                cursor.execute(
                    "INSERT INTO assignment_table (user_id, car_id, project_id, startDate, endDate, year, extra1, extra2, extra3, ort, group_id, hinweis, abwesend) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        user_id,
                        car_id,
                        project_id,
                        startDate,
                        endDate,
                        year,
                        extra1,
                        extra2,
                        extra3,
                        location,
                        next_group_id,
                        hinweis,
                        abw,
                    ),
                )

            conn.commit()
            print("Gruppen erfolgreich zugewiesen.")
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        finally:
            conn.close()
        return "Gruppe erfolgreich zugewiesen."
    else:
        return "Fehler beim Zuweisen der Gruppen."


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

    # Perform database operation to create a new customer with the provided inputs
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

    # Perform database operation to create a new project with the provided inputs
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

    try:
        cursor.execute("DELETE FROM users WHERE user_id=?", (personal_nr,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Mitarbeiter erfolgreich entfernt."


@app.route("/submit_c_delete", methods=["POST"])
def delete_customer():
    customer_id = request.form.get("kunden-delete")

    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM customers WHERE customer_id=?", (customer_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Kunde erfolgreich entfernt."


@app.route("/submit_car_delete", methods=["POST"])
def delete_car():
    car_id = request.form.get("car-delete")

    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM cars WHERE car_id=?", (car_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Auto erfolgreich entfernt."


@app.route("/submit_p_delete", methods=["POST"])
def delete_project():
    project_id = request.form.get("project-delete")

    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM projects WHERE project_id=?", (project_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Projekt erfolgreich entfernt."


@app.route("/delete_assignment", methods=["POST"])
def delete_assignment():
    assignment_id = request.form.get("assignmentId")

    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM assignment_table WHERE assignment_id=?", (assignment_id,)
        )
        conn.commit()
        result = {"status": "success"}
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        result = {"status": "error"}

    conn.close()
    return jsonify(result)


class LoginForm(FlaskForm):
    username = StringField("Username", [validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])
    submit = SubmitField("Login")


if __name__ == "__main__":
    app.run(debug=True)


# class CompanyOverviewApp(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("Einsatzplan")
#         self.geometry("800x600")
#         self.login_frame = LoginFrame(self)
#         self.login_frame.pack(fill=tk.BOTH, expand=True)

#         self.users = {"admin": "admin", "user": "123"}

#     def show_main_frame(self, user_role):
#         self.login_frame.destroy()
#         self.main_frame = MainFrame(self, user_role)
#         self.main_frame.pack(fill=tk.BOTH, expand=True)

#         form = LoginForm()
#         self.main_frame.assign_frame = (
#             AssignFrame(self, self.users) if user_role == "admin" else None
#         )
#         self.main_frame.assign_frame.pack(
#             fill=tk.BOTH, expand=True
#         ) if self.main_frame.assign_frame else None


# class LoginFrame(tk.Frame):
#     def __init__(self, master):
#         super().__init__(master)
#         self.username_label = tk.Label(self, text="Username:", font=("Arial", 20))
#         self.username_label.pack()
#         self.username_entry = tk.Entry(self)
#         self.username_entry.pack()
#         self.password_label = tk.Label(self, text="Password:", font=("Arial", 20))
#         self.password_label.pack()
#         self.password_entry = tk.Entry(self, show="*")
#         self.password_entry.pack()
#         self.login_button = tk.Button(
#             self, text="Login", command=self.login, font=("Arial", 20)
#         )
#         self.login_button.pack()

#     def login(self):
#         username = self.username_entry.get()
#         password = self.password_entry.get()

#         if username in self.master.users and self.master.users[username] == password:
#             self.master.show_main_frame("user")
#             return jsonify({"status": "success"})
#         elif username == "admin" and password == "admin":
#             self.master.show_main_frame("admin")
#             return jsonify({"status": "success"})
#         else:
#             return jsonify({"status": "error"})


# class MainFrame(tk.Frame):
#     def __init__(self, master, user_role):
#         super().__init__(master)
#         self.user_role = user_role
#         self.user_assignments = {}  # Store user assignments here

#         self.usernames = [
#             "Thorsten",
#             "Timo B.",
#             "Adama",
#             "Daniel X.",
#             "Albert",
#             "Horst",
#             "Szymon",
#             "Hans-Peter",
#             "Igor",
#             "Marcel K.",
#             "Michael v. H.",
#             "Tim",
#             "Ray",
#             "Matthias G.",
#             "Franco M.",
#             "Raphael S.",
#             "Marc",
#             "Frank B.",
#             "Jenris P.",
#             "Matthias K.",
#             "Timo W.",
#             "Frank M.",
#             "Sabrina M.",
#             "Daniel M.",
#             "Sinan",
#         ]  # Fixed list of users

#         # Create the dictionary to store the groups
#         self.user_groups = {
#             "SCHLOSSER": [
#                 "Thorsten",
#                 "Timo B.",
#                 "Adama",
#                 "Daniel X.",
#                 "Albert",
#                 "Horst",
#             ],
#             "DREHER & FRÄSER": ["Szymon", "Hans-Peter"],
#             "ELEKTRIKER": ["Igor", "Marcel K.", "Michael v. H.", "Tim", "Ray"],
#             "FREIER MITARBEITER": ["Matthias G."],
#             "BÜRO": [
#                 "Franco M.",
#                 "Raphael S.",
#                 "Marc",
#                 "Frank B.",
#                 "Jenris P.",
#                 "Matthias K.",
#                 "Timo W.",
#                 "Frank M.",
#                 "Sabrina M.",
#                 "Daniel M.",
#             ],
#             "HAUSWART": ["Sinan"],
#         }

#         self.table_frame = TableFrame(self, self.usernames, self.user_groups)
#         self.table_frame.pack(fill=tk.BOTH, expand=True)

#         if self.user_role == "admin":
#             self.assign_frame = AssignFrame(self, self.usernames)
#             self.assign_frame.pack(fill=tk.BOTH, expand=True)


# class TableFrame(tk.Frame):
#     def __init__(self, master, usernames, user_groups):
#         super().__init__(master)

#         self.usernames = usernames
#         self.user_groups = user_groups

#         """ Passendes Datum zum Wochentag darüber anzeigen """

#         self.table = ttk.Treeview(
#             self, columns=("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag")
#         )
#         self.table.heading("#0", text="Name")
#         self.table.column("#0", width=100)

#         for day in self.table["columns"]:
#             self.table.heading(day, text=day)
#             self.table.column(day, width=200, minwidth=150)

#         # Insert the usernames and group names into the table
#         for group, group_usernames in self.user_groups.items():
#             parent = ""
#             if not self.table.exists(group):
#                 parent = ""
#                 self.table.insert(
#                     "",
#                     "end",
#                     text=group,
#                     values=[""] * len(self.table["columns"]),
#                     open=True,
#                 )
#             else:
#                 parent = group

#             for i, username in enumerate(group_usernames):
#                 self.table.insert(
#                     parent,
#                     "end",
#                     text=username,
#                     values=[""] * len(self.table["columns"]),
#                 )

#         self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


# class AssignFrame(tk.Frame):
#     def __init__(self, master, usernames):
#         super().__init__(master)
#         self.usernames = usernames
#         self.master = master

#         self.dropdown_label = tk.Label(self, text="Mitarbeiter:", font=("Arial", 20))
#         self.dropdown_label.pack()

#         self.dropdown = tk.StringVar(self)
#         self.dropdown.set(self.usernames[0])
#         self.user_dropdown = tk.OptionMenu(self, self.dropdown, *self.usernames)
#         self.user_dropdown.pack()

#         self.day_label = tk.Label(self, text="Wochentag:", font=("Arial", 20))
#         self.day_label.pack()

#         self.day_dropdown = tk.StringVar(self)
#         self.day_dropdown.set("Tag wählen")
#         self.day_menu = tk.OptionMenu(
#             self,
#             self.day_dropdown,
#             "Montag",
#             "Dienstag",
#             "Mittwoch",
#             "Donnerstag",
#             "Freitag",
#             "Samstag",
#             "Sonntag",
#         )
#         self.day_menu.pack()

#         self.site_label = tk.Label(self, text="Baustelle:", font=("Arial", 20))
#         self.site_label.pack()
#         self.site_entry = tk.Entry(self)
#         self.site_entry.pack()

#         self.car_label = tk.Label(self, text="Auto:", font=("Arial", 20))
#         self.car_label.pack()

#         self.car_dropdown = tk.StringVar(self)
#         self.car_dropdown.set("")
#         self.car_menu = tk.OptionMenu(
#             self,
#             self.car_dropdown,
#             "",
#             "T11 () HB-BE 384",
#             "T13 (5/24) HB-SL 344",
#             "T14 (4/23) HB-SL 554",
#             "T15 (7/23) HB-SL 25",
#             "BMW (2/24) HB-SL 133",
#         )
#         self.car_menu.pack()

#         self.assign_button = tk.Button(
#             self, text="Zuweisen", command=self.assign, font=("Arial", 20)
#         )
#         self.assign_button.pack()

#     def assign(self):
#         selected_user = self.dropdown.get()
#         day = self.day_dropdown.get()
#         site = self.site_entry.get()
#         car = self.car_dropdown.get()

#         # Check if the car is already assigned to another user on the same day
#         for user, assignments in self.master.user_assignments.items():
#             if (
#                 user != selected_user
#                 and day in assignments
#                 and assignments[day].endswith(car)
#             ):
#                 messagebox.showerror(
#                     "Assign Error",
#                     f"Das Auto {car} ist bereits am {day} von {user} belegt.",
#                 )
#                 return

#         if selected_user not in self.master.user_assignments:
#             self.master.user_assignments[selected_user] = {}

#         self.master.user_assignments[selected_user][day] = f"{site}, {car}"

#         self.update_table(selected_user)

#         messagebox.showinfo("Assign", "Mitarbeiter erfolgreich zugewiesen.")

#     def update_table(self, user):
#         for day in self.master.user_assignments[user]:
#             item_id = None
#             for item in self.master.table_frame.table.get_children():
#                 if self.master.table_frame.table.item(item, "text") == user:
#                     item_id = item
#                     break

#             if item_id is not None:
#                 self.master.table_frame.table.set(
#                     item_id, day, self.master.user_assignments[user][day]
#                 )
