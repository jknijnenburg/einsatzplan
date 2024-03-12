import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from tkinter import Label
import tkinter.font as tkFont
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask import g, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
import sqlite3
import uuid
import json
from datetime import datetime, timedelta
import locale
import math
import holidays
import pymssql

app = Flask(__name__)

app.config["SECRET_KEY"] = "your_secret_key"

app.config["DATABASE"] = "SLT_EINSATZPLAN"

conn = pymssql.connect(
    host=r"10.10.100.106",
    port=r"1433",
    user=r"S-EINSATZPLAN",
    password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
    database="SLT_EINSATZPLAN",
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM assignment_table")
rows = cursor.fetchall()

cursor.close()
conn.close()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = pymssql.connect(
            host=r"10.10.100.106",
            port=r"1433",
            user=r"S-EINSATZPLAN",
            password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
            database=current_app.config["DATABASE"]
        )
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


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
    user_role = session.get("user_role", "user")  # Get user role from session

    current_week_number = get_current_week_number()
    week_number1 = int(request.args.get("week_number1", 0))  # only for the assignments
    week_number2 = int(request.args.get("week_number2", 1))
    today_date = datetime.now()

    today_date_meetings = datetime.now().date()

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

    meetings_data = db.execute(
        "SELECT m.m_group, m.date, m.startTime, m.endTime, m.room, m.service, GROUP_CONCAT(u.user_id) as user_ids FROM meetings m JOIN users u ON m.user_id = u.user_id WHERE m.date >= ? GROUP BY m.m_group, m.date, m.startTime, m.endTime, m.room, m.service ORDER BY m.date ASC LIMIT 4",
        (today_date_meetings,),
    ).fetchall()

    extra_data = db.execute("SELECT * FROM extras")
    extra_data1 = db.execute("SELECT * FROM extras")
    extra_data2 = db.execute("SELECT * FROM extras")
    extra_data3 = db.execute("SELECT * FROM extras")
    extra_data4 = db.execute("SELECT * FROM extras")
    extra_data5 = db.execute("SELECT * FROM extras")
    extra_data6 = db.execute("SELECT * FROM extras")

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
        meetings_data=meetings_data,
        extra_table_data1=extra_data1,
        extra_table_data2=extra_data2,
        extra_table_data3=extra_data3,
        extra_table_data4=extra_data4,
        extra_table_data5=extra_data5,
        extra_table_data6=extra_data6,
        extra_table_data=extra_data,
    )


def authenticate(username, password):
    if username == "admin" and password == "tecod-tasuyi":
        return "admin"
    else:
        return "user"


@app.route("/login", methods=["POST"])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Perform authentication logic here, e.g., check credentials against a database
        # Perform authentication
        user_role = authenticate(username, password)

        # Set user role in session
        session["user_role"] = user_role

        return jsonify({"status": "success", "user_role": "admin"})
    else:
        return jsonify({"status": "error", "user_role": "user"})


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_role", None)  # Remove user role from session
    session.clear()
    return redirect(url_for("index"))


@app.route("/assign_mitarbeiter", methods=["POST"])
def assign_mitarbeiter():
    personal_nr = request.form.get("personal_nr")

    startDate = request.form.get("startDate")
    endDate = request.form.get("endDate")
    year = request.form.get("year")
    location = request.form.get("ort")

    project_id = request.form.get("project_id", 0)

    if project_id == "null" or project_id == 0 or project_id == "0":
        project_id = 0

    car_id = request.form.get("car_id")

    if car_id == "null":
        car_id = 0

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

    week_id = request.form.get("week_id")

    print(
        f"Received values: personal_nr={personal_nr}, startDate={startDate}, endDate={endDate}, year={year}, week_id={week_id}, project_id={project_id}, car_id={car_id},extra={extra1, extra2, extra3}, checkboxValue={abw}"
    )

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
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

        if car_id != 0 and car_id != "0":
            cursor.execute(
                "SELECT COUNT(*) FROM assignment_table WHERE car_id = ? AND startDate <= ? AND endDate >= ?",
                (car_id, endDate, startDate),
            )

            car_cnt = cursor.fetchone()[0]

            if car_cnt > 0:
                return "Auto ist bereits zugewiesen."

        cursor.execute(
            "SELECT project_name FROM projects WHERE project_id = ?",
            (project_id,),
        )

        project_name = cursor.fetchone()[0]

        # Insert the assignment into the database
        cursor.execute(
            "INSERT INTO assignment_table (user_id, car_id, project_id, startDate, endDate, year, week_id, extra1, extra2, extra3, ort, group_id, hinweis, abwesend, project_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                personal_nr,
                car_id,
                project_id,
                startDate,
                endDate,
                year,
                week_id,
                extra1,
                extra2,
                extra3,
                location,
                0,  # Weil nur ein einzelner Mitarbeiter hinzugefügt wird und er keine Gruppe hat
                hinweis,
                abw,
                project_name,
            ),
        )
        conn.commit()

        return "Mitarbeiter erfolgreich zugewiesen."
    except pymssql.Error as e:
        print(f"SQLite error: {e}")
        return "An error occurred while assigning the employee."
    finally:
        conn.close()


@app.route("/get_assignment_hinweis", methods=["POST"])
def get_assignment_hinweis():
    assignment_id = request.form.get("assignmentId")

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
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
        car_id = 0

    if extra1 == "null":
        extra1 = "no"

    if extra2 == "null":
        extra2 = "no"

    if extra3 == "null":
        extra3 = "no"

    abw = 0

    if project_id == "null" or project_id == 0 or project_id == "0":
        project_id = 0

    # Get the highest group_id from the database
    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT MAX(group_id) FROM assignment_table")
        max_group_id = cursor.fetchone()[0]
        if max_group_id is None:
            max_group_id = 0  # If there are no existing group_ids, start from 0

        # Increment the highest group_id for the next assignment
        next_group_id = max_group_id + 1
    except pymssql.Error as e:
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
        conn = pymssql.connect(
            host=r"sqlserver01.sltgmbh.com",
            port=r"1433",
            user=r"S-EINSATZPLAN",
            password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
            database="SLT_EINSATZPLAN",
        )
        cursor = conn.cursor()

        print(f"Received values: startDate={startDate}, endDate={endDate}, year={year}")

        try:
            print("Numeric User IDs after list:", numeric_user_ids)
            print("Next Group ID:", next_group_id)

            if car_id != 0 and car_id != "0":
                cursor.execute(
                    "SELECT COUNT(*) FROM assignment_table WHERE car_id = ? AND startDate <= ? AND endDate >= ? AND group_id != ?",
                    (car_id, endDate, startDate, next_group_id),
                )

                car_cnt = cursor.fetchone()[0]

                if car_cnt > 0:
                    return "Auto ist bereits in anderer Gruppe zugewiesen."

            cursor.execute(
                "SELECT project_name FROM projects WHERE project_id = ?",
                (project_id,),
            )

            project_name = cursor.fetchone()[0]

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
                    "INSERT INTO assignment_table (user_id, car_id, project_id, startDate, endDate, year, extra1, extra2, extra3, ort, group_id, hinweis, abwesend, project_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                        project_name,
                    ),
                )

            conn.commit()
            print("Gruppen erfolgreich zugewiesen.")
        except pymssql.Error as e:
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

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
    cursor = conn.cursor()

    print(
        f"Received values: personal_nr={personal_nr}, vorname={vorname}, nachname={nachname}, bereich={bereich}"
    )

    # Perform database operation to create a new user with the provided inputs
    try:

        if bereich == "null":
            return "Bereich darf nicht leer sein."

        cursor.execute(
            "INSERT INTO users (user_id, first_name, last_name, work_field) VALUES (?, ?, ?, ?)",
            (personal_nr, vorname, nachname, bereich),
        )
        conn.commit()
    except pymssql.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Mitarbeiter erfolgreich angelegt."


@app.route("/submit_c_add", methods=["POST"])
def create_new_customer():
    customer_id = request.form.get("customer_id")
    customer_name = request.form.get("customer_name")

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
    cursor = conn.cursor()

    # Perform database operation to create a new customer with the provided inputs
    try:
        cursor.execute(
            "INSERT INTO customers (customer_id, customer_name) VALUES (?, ?)",
            (customer_id, customer_name),
        )
        conn.commit()
    except pymssql.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Kunde erfolgreich angelegt."


@app.route("/submit_p_add", methods=["POST"])
def create_new_project():
    project_id = request.form.get("project_id")
    project_name = request.form.get("project_name")
    customer_id = request.form.get("customer_id")

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
    cursor = conn.cursor()

    # Perform database operation to create a new project with the provided inputs
    try:
        cursor.execute(
            "INSERT INTO projects (project_id, project_name, customer_id) VALUES (?, ?, ?)",
            (project_id, project_name, customer_id),
        )
        conn.commit()
    except pymssql.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Projekt erfolgreich angelegt."


@app.route("/submit_car_add", methods=["POST"])
def create_new_car():
    car_name = request.form.get("car_id")

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
    cursor = conn.cursor()

    # Perform database operation to create a new project with the provided inputs
    try:
        cursor.execute("SELECT MAX(car_id) FROM cars")
        max_car_id = cursor.fetchone()[0]
        if max_car_id is None:
            max_car_id = 0  # If there are no existing group_ids, start from 0

        # Increment the highest group_id for the next assignment
        next_car_id = max_car_id + 1

        cursor.execute(
            "INSERT INTO cars (car_id, car_name) VALUES (?, ?)",
            (next_car_id, car_name),
        )
        conn.commit()
    except pymssql.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Auto erfolgreich hinzugefügt."


@app.route("/submit_e_add", methods=["POST"])
def create_new_extra():
    id = request.form.get("extra_id")
    name = request.form.get("extra_name")

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO extras (id, extra_name) VALUES (?, ?)", (id, name))
        conn.commit()
    except pymssql.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Extra erfolgreich hinzugefügt."


@app.route("/submit_m_delete", methods=["POST"])
def delete_user():
    personal_nr = request.form.get("personal_nr")

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM users WHERE user_id=?", (personal_nr,))
        conn.commit()
    except pymssql.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Mitarbeiter erfolgreich entfernt."


@app.route("/submit_c_delete", methods=["POST"])
def delete_customer():
    customer_id = request.form.get("kunden-delete")

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM customers WHERE customer_id=?", (customer_id,))
        conn.commit()
    except pymssql.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Kunde erfolgreich entfernt."


@app.route("/submit_car_delete", methods=["POST"])
def delete_car():
    car_id = request.form.get("car-delete")

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM cars WHERE car_id=?", (car_id,))
        conn.commit()
    except pymssql.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Auto erfolgreich entfernt."


@app.route("/submit_p_delete", methods=["POST"])
def delete_project():
    project_id = request.form.get("project-delete")

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM projects WHERE project_id=?", (project_id,))
        conn.commit()
    except pymssql.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Projekt erfolgreich entfernt."


@app.route("/submit_extra_delete", methods=["POST"])
def delete_extra():
    extra_id = request.form.get("extra-delete")

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM extras WHERE id=?", (extra_id,))
        conn.commit()
    except pymssql.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return "Extra erfolgreich entfernt."


@app.route("/delete_assignment", methods=["POST"])
def delete_assignment():
    assignment_id = request.form.get("assignmentId")

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM assignment_table WHERE assignment_id=?", (assignment_id,)
        )
        conn.commit()
        result = {"status": "success"}
    except pymssql.Error as e:
        print(f"SQLite error: {e}")
        result = {"status": "error"}

    conn.close()
    return jsonify(result)


@app.route("/belegungsplan")
def belegungsplan():
    db = get_db()
    form = LoginForm()
    user_role = request.args.get("user_role", "user")
    cursor = db.execute("SELECT * FROM users ORDER BY user_id")
    users = cursor.fetchall()

    # Fetch meetings with distinct m_group and associated user_ids
    meetings_data = db.execute(
        "SELECT m.m_group, m.date, m.startTime, m.endTime, m.room, m.service, GROUP_CONCAT(u.user_id) as user_ids FROM meetings m JOIN users u ON m.user_id = u.user_id GROUP BY m.m_group, m.date, m.startTime, m.endTime, m.room, m.service ORDER BY m.date DESC"
    ).fetchall()

    current_week_number = get_current_week_number()
    today_date = datetime.now()

    return render_template(
        "belegungsplan.html",
        form=form,
        user_role=user_role,
        current_week_number=current_week_number,
        today_date=today_date,
        users=users,
        meetings_data=meetings_data,
    )


@app.route("/reserve_meeting", methods=["POST"])
def reserve_meeting():
    try:
        # Extract form data
        date = request.form.get("date")
        start_time = request.form.get("startTime")
        end_time = request.form.get("endTime")
        room = request.form.get("room")
        services = request.form.getlist("services")

        personal_nr_list = request.form.getlist("personal_nr_list")

        participants_list = [
            int(user_id) for user_id in ",".join(personal_nr_list).split(",")
        ]

        # Insert data into the database
        conn = pymssql.connect(
            host=r"sqlserver01.sltgmbh.com",
            port=r"1433",
            user=r"S-EINSATZPLAN",
            password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
            database="SLT_EINSATZPLAN",
        )
        cursor = conn.cursor()

        print(
            f"Received values: participants_list={participants_list}, date={date}, startTime={start_time}, endTime={end_time}, room={room}, services={services}"
        )

        try:
            cursor.execute("SELECT MAX(m_group) FROM meetings")
            max_meeting_id = cursor.fetchone()[0]
            if max_meeting_id is None:
                max_meeting_id = 0  # If there are no existing group_ids, start from 0

            # Increment the highest group_id for the next assignment
            next_meeting_id = max_meeting_id + 1
        except pymssql.Error as e:
            print(f"SQLite error: {e}")
            next_meeting_id = (
                None  # Handle the case where there's an error getting the group_id
            )
        finally:
            conn.close()

            if next_meeting_id is not None:
                # Remove duplicate user IDs
                participants_list = list(set(participants_list))

                # Insert meeting for each user in participants_list
                conn = pymssql.connect(
                    host=r"sqlserver01.sltgmbh.com",
                    port=r"1433",
                    user=r"S-EINSATZPLAN",
                    password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
                    database="SLT_EINSATZPLAN",
                )
                cursor = conn.cursor()
                try:
                    print("Participants IDs after list:", participants_list)
                    print("Next Meeting ID:", next_meeting_id)

                    for participant in participants_list:
                        cursor.execute(
                            "INSERT INTO meetings (user_id, date, startTime, endTime, room, service, m_group) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (
                                participant,
                                date,
                                start_time,
                                end_time,
                                room,
                                ", ".join(services),
                                next_meeting_id,
                            ),
                        )

                    conn.commit()
                    print("Meeting erfolgreich erstellt.")
                except pymssql.Error as e:
                    print(f"SQLite error: {e}")
                finally:
                    conn.close()
                    return jsonify(
                        {
                            "status": "success",
                            "message": "Meeting reserved successfully",
                        }
                    )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/delete_meeting", methods=["POST"])
def delete_meeting():
    m_group = request.json.get("m_group")

    conn = pymssql.connect(
        host=r"10.10.100.106",
        port=r"1433",
        user=r"S-EINSATZPLAN",
        password=r"&H&^1c2M':Rq2-!_H77;_Kh28pz3^NwB",
        database="SLT_EINSATZPLAN",
    )
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM meetings WHERE m_group=?", (m_group,))
        conn.commit()
    except pymssql.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

    return jsonify({"status": "success"})


class LoginForm(FlaskForm):
    username = StringField("Username", [validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])
    submit = SubmitField("Login")


if __name__ == "__main__":
    app.run(debug=True)
