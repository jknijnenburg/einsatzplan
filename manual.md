# Company Overview Software User Manual

## Introduction

The Company Overview Software is a simple web-based application that provides a table view of a company's daily assignments for its colleagues. The table displays the days of the current week as columns and the names of the colleagues as rows. Each colleague can be assigned to a construction site for each day and can have a car assigned to them. Users with the admin role can assign colleagues these attributes, while users without admin privileges can only view their own assignments and the assignments of other colleagues.

## Installation

To use the Company Overview Software, you need to have Python installed on your system. You can download Python from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/)

Once Python is installed, you can follow these steps to install the required dependencies:

1. Open a command prompt or terminal.
2. Navigate to the directory where you have downloaded the Company Overview Software files.
3. Run the following command to install the dependencies:

```
pip install -r requirements.txt
```

## Usage

To start using the Company Overview Software, follow these steps:

1. Open a command prompt or terminal.
2. Navigate to the directory where you have downloaded the Company Overview Software files.
3. Run the following command to start the application:

```
python main.py
```

4. The application will open in a new window.
5. Enter your username and password in the login screen. If you are an admin, use "admin" as both the username and password. If you are a regular user, use any other username and password.
6. Click the "Login" button.
7. The main screen will display the company overview table.
8. If you are an admin, you will also see an "Assign" section where you can assign attributes to colleagues.
9. To assign attributes to a colleague, enter their name, the day, the construction site, and the car in the respective fields in the "Assign" section. Then click the "Assign" button.
10. The table will be updated with the assigned attributes.
11. Regular users can only view the table and cannot make any assignments.

## Troubleshooting

If you encounter any issues while using the Company Overview Software, please try the following troubleshooting steps:

1. Make sure you have installed Python and the required dependencies correctly.
2. Check that you are running the application from the correct directory.
3. Verify that you are entering the correct username and password.
4. If the table is not updating after making an assignment, try restarting the application.

If the issue persists, please contact our support team for further assistance.

## Conclusion

The Company Overview Software provides a simple and intuitive way to view and manage daily assignments for colleagues in a company. With the ability to assign construction sites and cars to colleagues, the software helps streamline the workflow and improve coordination within the organization. Whether you are an admin or a regular user, the software offers a user-friendly interface to access and update the company overview table.