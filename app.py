from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory, flash
from flask import g, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
import uuid
import json
from datetime import datetime, timedelta, time
from time import sleep
import locale
import math
import holidays
import pymssql
import os
from flask_caching import Cache

# debug mode
DEBUG = os.environ["DEBUG"]

# get configuration from App Settings / .env
SQL_SERVER = os.environ["SQL_SERVER"]
SQL_USER = os.environ["SQL_USER"]
SQL_PASSWORD = os.environ["SQL_PASSWORD"]
SQL_DATABASE = os.environ["SQL_DATABASE"]
print(SQL_SERVER)

# app
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# secret for flask CRSF
app.config["SECRET_KEY"] = "your_secret_key"

# change locale to DE
#locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
print(locale.getlocale())

# database connect retry
def retry_on_operational_error(func):
    def wrapper(*args, **kwargs):
        max_retries = 10
        retries = 0
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except pymssql.OperationalError as e:
                print(f"OperationalError: {e}. Retrying in 5 seconds...")
                sleep(5)
                retries += 1
        return jsonify({"status": "error",
                        "message": "Failed to connect to the database after multiple attempts."})
    
    return wrapper

# include static assets/fonts folder
@app.route('/assets/fonts/<filename>')
def assets_folder(filename):
    return send_from_directory('assets/fonts', filename)

# catch OperationalErrors on connect / SQL-Database in standby?
@retry_on_operational_error
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = pymssql.connect(
            host=SQL_SERVER,
            port=1433,
            user=SQL_USER,
            password=SQL_PASSWORD,
            database=SQL_DATABASE,
        )
    return db


#@app.teardown_appcontext
#def close_connection(exception):
#    db = getattr(g, "_database", None)
#    if db is not None:
#        db.close()


#@app.teardown_appcontext
#def close_db(error):
#    db = getattr(g, "_database", None)
#    if db is not None:
#        db.commit()


def get_current_week_number():
    today_date = datetime.now()
    return today_date.isocalendar()[
        1
    ]  # Extract the week number from the isocalendar tuple


def generate_week_dates(start_date):
    week_dates = [start_date + timedelta(days=i) for i in range(7)]
    return [date.strftime("%Y-%m-%d") for date in week_dates]


def generate_week_days(start_date):
    #locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
    week_days = [start_date + timedelta(days=i) for i in range(7)]
    return [date.strftime("%a") for date in week_days]


def authenticate_login(username, password):
    correct_username = "slt"
    correct_password = "einsatz54"

    return username == correct_username and password == correct_password

# Creates CalendarWeek entity
def ensureCalendarWeekExists(year, week_id):
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT week_id FROM CalendarWeek WHERE week_id = %d AND year = %d", 
            (week_id, year)
        )
        row = cur.fetchone()
        if not row:
            # calc begin, end of week
            start_date = datetime.fromisocalendar(int(year), int(week_id), 1)
            end_date = start_date + timedelta(days=6)
            cur.execute(
                "INSERT INTO CalendarWeek (week_id, year, startDate, endDate) VALUES (%d, %d, %s, %s)", 
                (week_id, year, start_date, end_date)
            )
            db.commit()
            # keep db open
    except Exception as e:
        print(f"SQL error: {e}")


# Login bevor der User auf die Webseite zugreifen kann
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if authenticate_login(username, password):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Falsche Login-Daten, bitte erneut versuchen.')
            return redirect(url_for('login'))
    
    return render_template('login.html', form=form)

@app.route('/logout', methods=["POST"])
def logout():
    session.pop("logged_in", False)
    session.clear()
    return redirect(url_for('login'))


@app.route("/")
@app.route("/index")
@cache.cached(timeout=300)
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users ORDER BY work_field")
    rows = cur.fetchall()
    cur.execute("SELECT * FROM assignment_table")
    assign_rows = cur.fetchall()
    cur.execute("SELECT * FROM customers")
    customer_rows = cur.fetchall()
    cur.execute("SELECT * FROM projects")
    project_rows = cur.fetchall()
    cur.execute("SELECT * FROM cars")
    car_rows = cur.fetchall()
    form = LoginForm()
    user_role = session.get("user_role", "user")  # Get user role from URL params

    today_date = datetime.now()
    current_week = today_date.isocalendar()[1]

    kw_1 = int(request.args.get("kw_1", current_week))
    kw_2 = kw_1 + 1

    if kw_2 > 53:
        kw_2 = 1

    year = today_date.year
    if kw_1 > current_week:
        year -= 1

    start_date1 = datetime.strptime(f'{year}-W{kw_1}-1', "%Y-W%W-%w")
    end_date1 = start_date1 + timedelta(days=6)

    start_date2 = datetime.strptime(f'{year}-W{kw_2}-1', "%Y-W%W-%w")
    end_date2 = start_date2 + timedelta(days=6)

    week_dates1 = generate_week_dates(start_date1)
    week_dates2 = generate_week_dates(start_date2)

    week_days1 = generate_week_days(start_date1)
    week_days2 = generate_week_days(start_date2)

    n_holidays = holidays.country_holidays(
        "DE", subdiv="HB", language="en_US", years=year
    )  # Feiertage in Bremen
    s_holidays = holidays.country_holidays(
        "DE", subdiv="BY", language="en_US", years=year
    )  # Bayern, da es die meisten Feiertage hat

    cur.execute(
        "SELECT TOP(4) m.m_group, m.date, m.startTime, m.endTime, m.room, m.service, STRING_AGG(u.user_id, ',') as user_ids FROM meetings m JOIN users u ON m.user_id = u.user_id WHERE m.date >= GETDATE() GROUP BY m.m_group, m.date, m.startTime, m.endTime, m.room, m.service ORDER BY m.date ASC",
    )
    meetings_data = cur.fetchall()

    cur.execute("SELECT * FROM extras")
    extra_data = cur.fetchall()

    return render_template(
        "index.html",
        data=rows,
        assignment_table_data=assign_rows,
        customer_table_data=customer_rows,
        project_table_data=project_rows,
        car_table_data=car_rows,
        form=form,
        user_role=user_role,
        current_week=current_week,
        kw_1=kw_1,
        kw_2=kw_2,
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
        extra_table_data1=extra_data,
        extra_table_data2=extra_data,
        extra_table_data3=extra_data,
        extra_table_data4=extra_data,
        extra_table_data5=extra_data,
        extra_table_data6=extra_data,
        extra_table_data=extra_data,
    )

def authenticate(username, password):
    if username == "admin" and password == "tecod-tasuyi":
        return "admin"
    else:
        return "user"


@app.route("/login_admin", methods=["POST"])
def login_admin():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Perform authentication
        user_role = authenticate(username, password)

        # Set user role in session
        session["user_role"] = user_role

        return jsonify({"status": "success", "user_role": "admin"})
    else:
        return jsonify({"status": "error", "user_role": "user"})


@app.route("/logout_admin", methods=["POST"])
def logout_admin():
    session.pop("user_role", None)  # Remove user role from session
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

    db = get_db()
    cur = db.cursor()

    try:
        # Check if the user already has an entry between the startDate and endDate
        cur.execute(
            "SELECT COUNT(*) FROM assignment_table WHERE user_id = %d AND startDate <= %s AND endDate >= %s",
            (personal_nr, endDate, startDate),
        )
        count = cur.fetchone()[0]

        if count > 0:
            return "Der Mitarbeiter hat schon eine Zuteilung zwischen dem ausgewählten Datum."

        # Check if the assignment already exists
        cur.execute(
            "SELECT COUNT(*) FROM assignment_table WHERE user_id = %d AND startDate = %s AND endDate = %s",
            (personal_nr, startDate, endDate),
        )
        count = cur.fetchone()[0]

        if count > 0:
            return "Die Zuteilung existiert bereits."

        if car_id != 0 and car_id != "0":
            cur.execute(
                "SELECT COUNT(*) FROM assignment_table WHERE car_id = %d AND startDate <= %s AND endDate >= %s",
                (car_id, endDate, startDate),
            )

            car_cnt = cur.fetchone()[0]

            if car_cnt > 0:
                return "Auto ist bereits zugewiesen."

        cur.execute(
            "SELECT project_name FROM projects WHERE project_id = %d",
            (project_id,),
        )

        project_name = cur.fetchone()[0]

        # ensure CalendarWeek exists
        ensureCalendarWeekExists(year, week_id)

        group_id = 0

        # Insert the assignment into the database
        cur.execute(
            "INSERT INTO assignment_table (user_id, car_id, project_id, startDate, endDate, year, week_id, extra1, extra2, extra3, ort, group_id, hinweis, abwesend, project_name) VALUES (%d, %d, %d, %s, %s, %d, %d, %s, %s, %s, %s, %d, %s, %d, %s)",
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
                group_id,  # Weil nur ein einzelner Mitarbeiter hinzugefügt wird und er keine Gruppe hat
                hinweis,
                abw,
                project_name,
            ),
        )
        db.commit()

        return "Mitarbeiter erfolgreich zugewiesen."
    except pymssql.Error as e:
        print(f"SQL error: {e}")
        return "An error occurred while assigning the employee."
    finally:
        db.close()

@app.route("/assign_mitarbeiter_bulk", methods=["POST"])
def assign_mitarbeiter_bulk():
    assignments = request.json
    db = get_db()
    cur = db.cursor()

    try:
        for assignment in assignments:
            personal_nr = assignment['personal_nr']
            startDate = assignment['startDate']
            endDate = assignment['endDate']
            year = assignment['year']
            week_id = assignment['week_id']
            project_id = assignment['project_id']
            car_id = assignment['car_id']
            extra1 = assignment['extra1']
            extra2 = assignment['extra2']
            extra3 = assignment['extra3']
            location = assignment['ort']
            hinweis = assignment['hinweis']
            abw = assignment['checkedRadioButton']

            # Check if the user already has an entry between the startDate and endDate
            cur.execute(
                "SELECT COUNT(*) FROM assignment_table WHERE user_id = %d AND startDate <= %s AND endDate >= %s",
                (personal_nr, endDate, startDate),
            )
            count = cur.fetchone()[0]

            if count > 0:
                return jsonify({"error": f"Der Mitarbeiter {personal_nr} hat schon eine Zuteilung zwischen dem ausgewählten Datum."}), 400

            if car_id != 0 and car_id != "0":
                cur.execute(
                    "SELECT COUNT(*) FROM assignment_table WHERE car_id = %d AND startDate <= %s AND endDate >= %s",
                    (car_id, endDate, startDate),
                )
                car_cnt = cur.fetchone()[0]

                if car_cnt > 0:
                    return jsonify({"error": "Auto ist bereits zugewiesen."}), 400

            cur.execute(
                "SELECT project_name FROM projects WHERE project_id = %d",
                (project_id,),
            )
            project_name = cur.fetchone()[0]

            # ensure CalendarWeek exists
            ensureCalendarWeekExists(year, week_id)

            # Insert the assignment into the database
            cur.execute(
                """INSERT INTO assignment_table 
                (user_id, car_id, project_id, startDate, endDate, year, week_id, 
                extra1, extra2, extra3, ort, group_id, hinweis, abwesend, project_name) 
                VALUES (%d, %d, %d, %s, %s, %d, %d, %s, %s, %s, %s, %d, %s, %d, %s)""",
                (personal_nr, car_id, project_id, startDate, endDate, year, week_id,
                 extra1, extra2, extra3, location, 0, hinweis, abw, project_name)
            )

        db.commit()
        return jsonify({"message": "Assignments created successfully"}), 200
    except pymssql.Error as e:
        print(f"SQL error: {e}")
        return jsonify({"error": "An error occurred while creating assignments"}), 500
    finally:
        db.close()



@app.route("/get_assignment_hinweis", methods=["POST"])
def get_assignment_hinweis():
    assignment_id = request.form.get("assignmentId")

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT hinweis FROM assignment_table WHERE assignment_id=%d", (assignment_id,)
    )
    result = cur.fetchone()

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
    week_id = request.form.get("week_id")
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
    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("SELECT MAX(group_id) FROM assignment_table")
        max_group_id = cur.fetchone()[0]
        if max_group_id is None:
            max_group_id = 0  # If there are no existing group_ids, start from 0

        # Increment the highest group_id for the next assignment
        next_group_id = max_group_id + 1
    except pymssql.Error as e:
        print(f"SQL error: {e}")
        next_group_id = (
            None  # Handle the case where there's an error getting the group_id
        )

    if next_group_id is not None:
        # Remove duplicate user IDs
        numeric_user_ids = list(set(numeric_user_ids))

        # Insert assignments for each user in numeric_user_ids
        print(f"Received values: startDate={startDate}, endDate={endDate}, year={year}")

        try:
            print("Numeric User IDs after list:", numeric_user_ids)
            print("Next Group ID:", next_group_id)

            if car_id != 0 and car_id != "0":
                cur.execute(
                    "SELECT COUNT(*) FROM assignment_table WHERE car_id = %d AND startDate <= %s AND endDate >= %s AND group_id != %d",
                    (car_id, endDate, startDate, next_group_id),
                )

                car_cnt = cur.fetchone()[0]

                if car_cnt > 0:
                    return "Auto ist bereits in anderer Gruppe zugewiesen."

            cur.execute(
                "SELECT project_name FROM projects WHERE project_id = %d",
                (project_id,),
            )

            project_name = cur.fetchone()[0]

            for user_id in numeric_user_ids:
                cur.execute(
                    "SELECT COUNT(*) FROM assignment_table WHERE user_id = %d AND startDate <= %s AND endDate >= %s",
                    (user_id, endDate, startDate),
                )
                count = cur.fetchone()[0]

                if count > 0:
                    return (
                        "Der Mitarbeiter "
                        + f"{user_id}"
                        + " hat schon eine Zuteilung zwischen dem ausgewählten Datum."
                    )

                # ensure CalendarWeek exists
                ensureCalendarWeekExists(year, week_id)

                cur.execute(
                    "INSERT INTO assignment_table (user_id, car_id, project_id, startDate, endDate, year, week_id, extra1, extra2, extra3, ort, group_id, hinweis, abwesend, project_name) VALUES (%d, %d, %d, %s, %s, %d, %d, %s, %s, %s, %s, %d, %s, %d, %s)",
                    (
                        user_id,
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
                        next_group_id,
                        hinweis,
                        abw,
                        project_name,
                    ),
                )

            db.commit()
            print("Gruppen erfolgreich zugewiesen.")
        except pymssql.Error as e:
            print(f"SQL error: {e}")
        finally:
            db.close()
        return "Gruppe erfolgreich zugewiesen."
    else:
        return "Fehler beim Zuweisen der Gruppen."

@app.route("/assign_group_bulk", methods=["POST"])
def assign_group_bulk():
    group_assignments = request.json
    db = get_db()
    cur = db.cursor()

    try:
        for assignment in group_assignments:
            personal_nr_list = assignment['personal_nr_list']
            startDate = assignment['startDate']
            endDate = assignment['endDate']
            year = assignment['year']
            week_id = assignment['week_id']
            project_id = assignment['project_id']
            car_id = assignment['car_id']
            location = assignment['ort']
            extra1 = assignment['extra1']
            extra2 = assignment['extra2']
            extra3 = assignment['extra3']
            hinweis = assignment['hinweis']

            # Get the highest group_id from the database
            cur.execute("SELECT MAX(group_id) FROM assignment_table")
            max_group_id = cur.fetchone()[0]
            if max_group_id is None:
                max_group_id = 0

            next_group_id = max_group_id + 1

            # Check for car assignment conflicts
            if car_id != 0 and car_id != "0":
                cur.execute(
                    "SELECT COUNT(*) FROM assignment_table WHERE car_id = %d AND startDate <= %s AND endDate >= %s AND group_id != %d",
                    (car_id, endDate, startDate, next_group_id),
                )
                car_cnt = cur.fetchone()[0]
                if car_cnt > 0:
                    return jsonify({"error": "Auto ist bereits in anderer Gruppe zugewiesen."}), 400

            # Get project name
            cur.execute(
                "SELECT project_name FROM projects WHERE project_id = %d",
                (project_id,),
            )
            project_name = cur.fetchone()[0]

            for user_id in personal_nr_list:
                # Check for user assignment conflicts
                cur.execute(
                    "SELECT COUNT(*) FROM assignment_table WHERE user_id = %d AND startDate <= %s AND endDate >= %s",
                    (user_id, endDate, startDate),
                )
                count = cur.fetchone()[0]
                if count > 0:
                    return jsonify({"error": f"Der Mitarbeiter {user_id} hat schon eine Zuteilung zwischen dem ausgewählten Datum."}), 400

                # Ensure CalendarWeek exists
                ensureCalendarWeekExists(year, week_id)

                # Insert the assignment
                cur.execute(
                    """INSERT INTO assignment_table 
                    (user_id, car_id, project_id, startDate, endDate, year, week_id, 
                    extra1, extra2, extra3, ort, group_id, hinweis, abwesend, project_name) 
                    VALUES (%d, %d, %d, %s, %s, %d, %d, %s, %s, %s, %s, %d, %s, %d, %s)""",
                    (user_id, car_id, project_id, startDate, endDate, year, week_id,
                     extra1, extra2, extra3, location, next_group_id, hinweis, 0, project_name)
                )

        db.commit()
        return jsonify({"message": "Gruppen erfolgreich zugewiesen."}), 200
    except pymssql.Error as e:
        db.rollback()
        print(f"SQL error: {e}")
        return jsonify({"error": "Ein Fehler ist aufgetreten beim Zuweisen der Gruppen."}), 500
    finally:
        db.close()



@app.route("/submit_m_add", methods=["POST"])
def create_new_user():
    personal_nr = request.form.get("personal_nr")
    vorname = request.form.get("vorname")
    nachname = request.form.get("nachname")
    bereich = request.form.get("bereich")

    db = get_db()
    cur = db.cursor()

    print(
        f"Received values: personal_nr={personal_nr}, vorname={vorname}, nachname={nachname}, bereich={bereich}"
    )

    # Perform database operation to create a new user with the provided inputs
    try:

        if bereich == "null":
            return "Bereich darf nicht leer sein."

        cur.execute(
            "INSERT INTO users (user_id, first_name, last_name, work_field) VALUES (%d, %s, %s, %s)",
            (personal_nr, vorname, nachname, bereich),
        )
        db.commit()
    except pymssql.Error as e:
        print(f"SQL error: {e}")
    finally:
        db.close()

    return "Mitarbeiter erfolgreich angelegt."


@app.route("/submit_c_add", methods=["POST"])
def create_new_customer():
    customer_id = request.form.get("customer_id")
    customer_name = request.form.get("customer_name")

    db = get_db()
    cur = db.cursor()

    # Perform database operation to create a new customer with the provided inputs
    try:
        cur.execute(
            "INSERT INTO customers (customer_id, customer_name) VALUES (%d, %s)",
            (customer_id, customer_name),
        )
        db.commit()
    except pymssql.Error as e:
        print(f"SQL error: {e}")
    finally:
        db.close()

    return "Kunde erfolgreich angelegt."


@app.route("/submit_p_add", methods=["POST"])
def create_new_project():
    project_id = request.form.get("project_id")
    project_name = request.form.get("project_name")
    customer_id = request.form.get("customer_id")

    db = get_db()
    cur = db.cursor()

    # Perform database operation to create a new project with the provided inputs
    try:
        cur.execute(
            "INSERT INTO projects (project_id, project_name, customer_id) VALUES (%d, %s, %d)",
            (project_id, project_name, customer_id),
        )
        db.commit()
    except pymssql.Error as e:
        print(f"SQL error: {e}")
    finally:
        db.close()

    return "Projekt erfolgreich angelegt."


@app.route("/submit_car_add", methods=["POST"])
def create_new_car():
    car_name = request.form.get("car_id")

    db = get_db()
    cur = db.cursor()

    # Perform database operation to create a new project with the provided inputs
    try:
        cur.execute("SELECT MAX(car_id) FROM cars")
        max_car_id = cur.fetchone()[0]
        if max_car_id is None:
            max_car_id = 0  # If there are no existing group_ids, start from 0

        # Increment the highest group_id for the next assignment
        next_car_id = max_car_id + 1

        cur.execute(
            "INSERT INTO cars (car_id, car_name) VALUES (%d, %s)",
            (next_car_id, car_name),
        )
        db.commit()
    except pymssql.Error as e:
        print(f"SQL error: {e}")
    finally:
        db.close()

    return "Auto erfolgreich hinzugefügt."


@app.route("/submit_e_add", methods=["POST"])
def create_new_extra():
    id = request.form.get("extra_id")
    name = request.form.get("extra_name")

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("INSERT INTO extras (id, extra_name) VALUES (%s, %s)", (id, name))
        db.commit()
    except pymssql.Error as e:
        print(f"SQL error: {e}")
    finally:
        db.close()

    return "Extra erfolgreich hinzugefügt."


@app.route("/submit_m_delete", methods=["POST"])
def delete_user():
    personal_nr = request.form.get("personal_nr")

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("DELETE FROM users WHERE user_id=%d", (personal_nr,))
        db.commit()
    except pymssql.Error as e:
        print(f"SQL error: {e}")
    finally:
        db.close()

    return "Mitarbeiter erfolgreich entfernt."


@app.route("/submit_c_delete", methods=["POST"])
def delete_customer():
    customer_id = request.form.get("kunden-delete")

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("DELETE FROM customers WHERE customer_id=%d", (customer_id,))
        db.commit()
    except pymssql.Error as e:
        print(f"SQL error: {e}")
    finally:
        db.close()

    return "Kunde erfolgreich entfernt."


@app.route("/submit_car_delete", methods=["POST"])
def delete_car():
    car_id = request.form.get("car-delete")

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("DELETE FROM cars WHERE car_id=%d", (car_id,))
        db.commit()
    except pymssql.Error as e:
        print(f"SQL error: {e}")
    finally:
        db.close()

    return "Auto erfolgreich entfernt."


@app.route("/submit_p_delete", methods=["POST"])
def delete_project():
    project_id = request.form.get("project-delete")

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("DELETE FROM projects WHERE project_id=%d", (project_id,))
        db.commit()
    except pymssql.Error as e:
        print(f"SQL error: {e}")
    finally:
        db.close()

    return "Projekt erfolgreich entfernt."


@app.route("/submit_extra_delete", methods=["POST"])
def delete_extra():
    extra_id = request.form.get("extra-delete")

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("DELETE FROM extras WHERE id=%s", (extra_id,))
        db.commit()
    except pymssql.Error as e:
        print(f"SQL error: {e}")
    finally:
        db.close()

    return "Extra erfolgreich entfernt."


@app.route("/delete_assignment", methods=["POST"])
def delete_assignment():
    assignment_id = request.form.get("assignmentId")

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute(
            "DELETE FROM assignment_table WHERE assignment_id=%d", (assignment_id,)
        )
        db.commit()
        result = {"status": "success"}
    except pymssql.Error as e:
        print(f"SQL error: {e}")
        result = {"status": "error"}

    db.close()
    return jsonify(result)


@app.route("/belegungsplan")
def belegungsplan():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    db = get_db()
    cur = db.cursor()
    form = LoginForm()
    user_role = request.args.get("user_role", "user")

    cur.execute("SELECT * FROM users ORDER BY user_id")
    users = cur.fetchall()

    # Fetch meetings with distinct m_group and associated user_ids
    cur.execute(
        "SELECT m.m_group, m.date, m.startTime, m.endTime, m.room, m.service, STRING_AGG(u.user_id, ',') as user_ids FROM meetings m JOIN users u ON m.user_id = u.user_id GROUP BY m.m_group, m.date, m.startTime, m.endTime, m.room, m.service ORDER BY m.date DESC"
    )
    meetings_data = cur.fetchall()

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
        services = request.form.get("services")

        personal_nr_list = request.form.getlist("personal_nr_list")

        participants_list = [
            int(user_id) for user_id in ",".join(personal_nr_list).split(",")
        ]

        # Insert data into the database
        db = get_db()
        cur = db.cursor()

        print(
            f"Received values: participants_list={participants_list}, date={date}, startTime={start_time}, endTime={end_time}, room={room}, services={services}"
        )

        cur.execute("SELECT MAX(m_group) FROM meetings")
        max_meeting_id = cur.fetchone()[0]
        if max_meeting_id is None:
            max_meeting_id = 0  # If there are no existing group_ids, start from 0

        # Increment the highest group_id for the next assignment
        next_meeting_id = max_meeting_id + 1

        if next_meeting_id is not None:
            # Remove duplicate user IDs
            participants_list = list(set(participants_list))

            # Insert meeting for each user in participants_list
            db = get_db()
            cur = db.cursor()

            print("Participants IDs after list:", participants_list)
            print("Next Meeting ID:", next_meeting_id)

            for participant in participants_list:
                print(participant, date, start_time, end_time, room, services, next_meeting_id)
                cur.execute(
                    "INSERT INTO meetings (user_id, date, startTime, endTime, room, service, m_group) VALUES (%d, %s, %s, %s, %s, %s, %d)",
                    (
                        participant,
                        date,
                        start_time,
                        end_time,
                        room,
                        services,
                        next_meeting_id
                    )
                )

            db.commit()
            print("Meeting erfolgreich erstellt.")
            return jsonify({"status": "success","message": "Meeting reserved successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        db.close()

# Get assignment details
@app.route("/get_assignment_details/<int:assignment_id>")
def get_assignment_details(assignment_id):
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("""
            SELECT a.startDate, a.endDate, a.hinweis, a.user_id
            FROM assignment_table a
            WHERE a.assignment_id = %s OR a.group_id = (
                SELECT group_id FROM assignment_table WHERE assignment_id = %s
            )
        """, (assignment_id, assignment_id))
        assignments = cur.fetchall()
        
        if not assignments:
            return jsonify({"error": "Assignment not found"}), 404
        
        return jsonify({
            "start_date": assignments[0][0].strftime('%Y-%m-%d'),
            "end_date": assignments[0][1].strftime('%Y-%m-%d'),
            "hinweis": assignments[0][2],
            "employees": [a[3] for a in assignments]
        })
    except Exception as e:
        print(f"Error fetching assignment details: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        db.close()


# Edit existing assignment
@app.route("/edit_assignment", methods=["POST"])
def edit_assignment():
    assignment_id = request.form.get("assignment_id")
    new_start_date = request.form.get("start_date")
    new_end_date = request.form.get("end_date")
    new_hinweis = request.form.get("hinweis")
    new_employees = request.form.getlist("employees[]")

    db = get_db()
    cur = db.cursor()

    try:
        # Check for overlaps
        overlap_query = """
        SELECT user_id FROM assignment_table 
        WHERE user_id IN %s 
        AND ((startDate <= %s AND endDate >= %s) 
        OR (startDate <= %s AND endDate >= %s))
        AND assignment_id != %s
        AND group_id != (SELECT group_id FROM assignment_table WHERE assignment_id = %s)
        """
        cur.execute(overlap_query, (tuple(new_employees), new_end_date, new_start_date, new_start_date, new_end_date, assignment_id, assignment_id))
        overlaps = cur.fetchall()

        if overlaps:
            return jsonify({"status": "error", "message": "Overlap detected for employees: " + ", ".join([str(o[0]) for o in overlaps])})

        # Get the group_id
        cur.execute("SELECT group_id FROM assignment_table WHERE assignment_id = %s", (assignment_id,))
        group_id = cur.fetchone()[0]

        # Update all assignments in the group
        update_query = """
        UPDATE assignment_table 
        SET startDate = %s, endDate = %s, hinweis = %s
        WHERE group_id = %s
        """
        cur.execute(update_query, (new_start_date, new_end_date, new_hinweis, group_id))

        # Delete old employee assignments not in the new list
        cur.execute("DELETE FROM assignment_table WHERE group_id = %s AND user_id NOT IN %s", (group_id, tuple(new_employees)))

        # Insert new employee assignments
        for employee in new_employees:
            cur.execute("""
                INSERT INTO assignment_table (user_id, startDate, endDate, hinweis, group_id)
                SELECT %s, %s, %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM assignment_table WHERE group_id = %s AND user_id = %s
                )
            """, (employee, new_start_date, new_end_date, new_hinweis, group_id, group_id, employee))

        db.commit()
        return jsonify({"status": "success", "message": "Assignment updated successfully"})

    except Exception as e:
        db.rollback()
        print(f"Error updating assignment: {e}")
        return jsonify({"status": "error", "message": str(e)})
    finally:
        db.close()


@app.route("/delete_meeting", methods=["POST"])
def delete_meeting():
    m_group = request.json.get("m_group")

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("DELETE FROM meetings WHERE m_group=%d", (m_group,))
        db.commit()
    except pymssql.Error as e:
        print(f"SQL error: {e}")
    finally:
        db.close()

    return jsonify({"status": "success"})


class LoginForm(FlaskForm):
    username = StringField("Username", [validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])
    submit = SubmitField("Login")


if __name__ == '__main__':
    app.run(debug=DEBUG)