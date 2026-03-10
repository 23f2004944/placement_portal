# Placement Management System

A web-based **Placement Management Portal** built using **Flask, SQLite, and Bootstrap**.
This system allows **students, companies, and administrators** to manage placement drives, applications, and approvals in a centralized platform.

---

## Features

### Admin

* View dashboard statistics (students, companies, drives, applications)
* Approve or reject company registrations
* Blacklist companies
* Blacklist students
* Search students by **name or ID**
* Search companies by **company name**
* Mark placement drives as **completed**
* Reject placement drives
* View all ongoing placement drives

### Student

* Register and create profile
* Upload resume
* Edit profile information
* View available placement drives
* Apply to placement drives
* Track application status

### Company

* Register company profile
* Wait for admin approval
* Create placement drives
* Edit drive details
* View student applications
* Update application status (shortlisted / rejected)

---

## Tech Stack

* **Backend:** Flask (Python)
* **Database:** SQLite with SQLAlchemy ORM
* **Frontend:** HTML, Bootstrap 5
* **Templating Engine:** Jinja2

---

## Project Structure

```
placement_portal/
│
├── app.py
├── placement.db
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── admin_dashboard.html
│   ├── student_dashboard.html
│   ├── company_dashboard.html
│   ├── create_drive.html
│   ├── edit_profile.html
│   ├── applications.html
│   └── view_drives.html
│
└── static/
```

---

## Database Models

### Users

Stores login credentials and role.

Fields:

* id
* username
* password
* role (admin / student / company)

### Students

Stores student profile information.

Fields:

* id
* user_id
* name
* department
* resume
* is_blacklisted

### Companies

Stores company profile details.

Fields:

* id
* user_id
* company_name
* hr_contact
* status (approved or pending)
* is_blacklisted

### Drives

Stores placement drive details.

Fields:

* id
* company_id
* drive_name
* job_title
* job_description
* salary
* location
* deadline
* status (open/closed)
* is_rejected

### Applications

Stores student applications for drives.

Fields:

* id
* student_id
* drive_id
* status
* remark
* date

---

## Installation

### 1. Clone the repository

```
git clone https://github.com/your-username/placement-management-system.git
cd placement-management-system
```

### 2. Install dependencies

```
pip install flask flask_sqlalchemy
```

### 3. Run the application

```
python app.py
```

### 4. Open in browser

```
http://127.0.0.1:5000/
```

---

## Default Admin Login

```
Username: admin
Password: admin123
```

The admin account is automatically created when the application runs for the first time.
