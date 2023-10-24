import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from tkinter import Label
import tkinter.font as tkFont

class CompanyOverviewApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Einsatzplan")
        self.geometry("800x600")
        self.login_frame = LoginFrame(self)
        self.login_frame.pack(fill=tk.BOTH, expand=True)

        self.users = {
            "admin": "admin",
            "user": "123"
        }

    def show_main_frame(self, user_role):
        self.login_frame.destroy()
        self.main_frame = MainFrame(self, user_role)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.username_label = tk.Label(self, text="Username:", font=('Arial', 20))
        self.username_label.pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()
        self.password_label = tk.Label(self, text="Password:", font=('Arial', 20))
        self.password_label.pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()
        self.login_button = tk.Button(self, text="Login", command=self.login, font=('Arial', 20))
        self.login_button.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "admin":
            self.master.show_main_frame("admin")
        elif username in self.master.users and self.master.users[username] == password:
            self.master.show_main_frame("user")
        else:
            messagebox.showinfo("Login", "Falscher Nutzername oder Password.")

class MainFrame(tk.Frame):
    def __init__(self, master, user_role):
        super().__init__(master)
        self.user_role = user_role
        self.user_assignments = {}  # Store user assignments here

        self.usernames = ["Thorsten", "Timo B.", "Adama", "Daniel X.", "Albert", "Horst", "Szymon", "Hans-Peter", "Igor", "Marcel K.", "Michael v. H.", "Tim", "Ray", "Matthias G.", "Franco M.", "Raphael S.", "Marc", "Frank B.","Jenris P.", "Matthias K.", "Timo W.", "Frank M.", "Sabrina M.", "Daniel M.", "Sinan"]  # Fixed list of users
        
        # Create the dictionary to store the groups
        self.user_groups = {
            "SCHLOSSER": ["Thorsten", "Timo B.", "Adama", "Daniel X.", "Albert", "Horst"],
            "DREHER & FRÄSER": ["Szymon", "Hans-Peter"],
            "ELEKTRIKER": ["Igor", "Marcel K.", "Michael v. H.", "Tim", "Ray"],
            "FREIER MITARBEITER": ["Matthias G."],
            "BÜRO": ["Franco M.", "Raphael S.", "Marc", "Frank B.","Jenris P.", "Matthias K.", "Timo W.", "Frank M.", "Sabrina M.", "Daniel M."],
            "HAUSWART": ["Sinan"]
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
        """ KW irgendwo anzeigen """

        self.table = ttk.Treeview(self, columns=("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"))
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
                self.table.insert("", "end", text=group, values=[""] * len(self.table["columns"]), open=True)
            else:
                parent = group

            for i, username in enumerate(group_usernames):
                self.table.insert(parent, "end", text=username, values=[""] * len(self.table["columns"]))

        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

class AssignFrame(tk.Frame):
    def __init__(self, master, usernames):
        super().__init__(master)
        self.usernames = usernames
        self.master = master

        self.dropdown_label = tk.Label(self, text="Mitarbeiter:", font=('Arial', 20))
        self.dropdown_label.pack()

        self.dropdown = tk.StringVar(self)
        self.dropdown.set(self.usernames[0])
        self.user_dropdown = tk.OptionMenu(self, self.dropdown, *self.usernames)
        self.user_dropdown.pack()

        self.day_label = tk.Label(self, text="Wochentag:", font=('Arial', 20))
        self.day_label.pack()

        self.day_dropdown = tk.StringVar(self)
        self.day_dropdown.set("Tag wählen")
        self.day_menu = tk.OptionMenu(self, self.day_dropdown, "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")
        self.day_menu.pack()

        self.site_label = tk.Label(self, text="Baustelle:", font=('Arial', 20))
        self.site_label.pack()
        self.site_entry = tk.Entry(self)
        self.site_entry.pack()

        self.car_label = tk.Label(self, text="Auto:", font=('Arial', 20))
        self.car_label.pack()
        
        self.car_dropdown = tk.StringVar(self)
        self.car_dropdown.set("")
        self.car_menu = tk.OptionMenu(self, self.car_dropdown, "", "T11 () HB-BE 384", "T13 (5/24) HB-SL 344", "T14 (4/23) HB-SL 554", "T15 (7/23) HB-SL 25", "BMW (2/24) HB-SL 133")
        self.car_menu.pack()

        self.assign_button = tk.Button(self, text="Zuweisen", command=self.assign, font=('Arial', 20))
        self.assign_button.pack()

    def assign(self):
        selected_user = self.dropdown.get()
        day = self.day_dropdown.get()
        site = self.site_entry.get()
        car = self.car_dropdown.get()

        # Check if the car is already assigned to another user on the same day
        for user, assignments in self.master.user_assignments.items():
            if user != selected_user and day in assignments and assignments[day].endswith(car):
                messagebox.showerror("Assign Error", f"Das Auto {car} ist bereits am {day} von {user} belegt.")
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
                self.master.table_frame.table.set(item_id, day, self.master.user_assignments[user][day])

if __name__ == "__main__":
    app = CompanyOverviewApp()
    app.mainloop()
