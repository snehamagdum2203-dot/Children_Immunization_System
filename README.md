# Children Immunization System

A web-based system developed to manage children's vaccination records and help healthcare staff keep track of upcoming and missed vaccines.

## About the Project

The Children Immunization System is designed to replace the traditional paper-based vaccination record process with a digital system.

The system allows healthcare staff to register children, maintain their vaccination records, update vaccine information, search child records, and send vaccine reminders to parents.

## Features

- Staff Registration and Login
- Parent Login
- Hospital Login
- New Child Registration
- Digital Vaccination Records
- Update Vaccine Records
- Search Child Records
- Vaccine Reminder Management
- WhatsApp Vaccine Reminders
- Monthly Reports
- PDF Report Generation
- Vaccine Record Management

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- ReportLab
- Twilio WhatsApp API

## Project Structure

```text
children_immunization_system/
│
├── app.py
├── create_database.py
├── setup_db.py
├── migrate_db.py
├── database.db
│
├── templates/
│   ├── home.html
│   ├── staff_login.html
│   ├── staff_signup.html
│   ├── parent_login.html
│   ├── hospital_login.html
│   ├── staff_dashboard.html
│   ├── child_register.html
│   ├── update_vaccine.html
│   ├── reminder.html
│   └── report.html
│
└── README.md
