from flask import Flask, flash, redirect, render_template,request, session, url_for #session is a dictionary maintained by flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
app.secret_key = 'shraddha' #used to encrypt the session data
db=SQLAlchemy() 
db.init_app(app) 

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), nullable = False)
    password = db.Column(db.String(100), nullable = False)
    role = db.Column(db.String(20), nullable = False) #Admin, student or company

class Students(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    name = db.Column(db.String(100), nullable = False)
    department = db.Column(db.String(100), nullable = False)
    resume = db.Column(db.String(200), nullable = True) #path to resume file
    is_blacklisted = db.Column(db.Boolean, default = False) #blacklisted or not

class Companies(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    company_name = db.Column(db.String(100), nullable = False)
    hr_contact = db.Column(db.String(100), nullable = False)
    status = db.Column(db.Boolean, default=False)#approved, pending or blacklisted
    is_blacklisted = db.Column(db.Boolean, default = False) 

class Drives(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable = False)
    drive_name = db.Column(db.String(100), nullable = False)
    job_title = db.Column(db.String(100), nullable = False)
    job_description = db.Column(db.Text, nullable = False)
    salary = db.Column(db.String(50), nullable = False)
    location = db.Column(db.String(100), nullable = False)
    deadline = db.Column(db.DateTime, nullable = False)
    status = db.Column(db.Boolean, default=False) #open or closed
    is_rejected = db.Column(db.Boolean, default=False)

class Applications(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable = False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drives.id'), nullable = False)
    status = db.Column(db.String(20), default='applied') #applied, shortlisted, rejected
    remark = db.Column(db.Text, nullable = True)
    date = db.Column(db.DateTime)


with app.app_context(): 
    db.create_all()
    admin = Users.query.filter_by(username='admin').first()
    if not admin:
        users = Users(username='admin', password='admin123', role='admin')
        db.session.add(users)
        db.session.commit()   

#index page
@app.route("/", methods = ['GET', 'POST'])
def home():
    return render_template("index.html")

#login page
@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username, password = password).first() #filter_by used in place for where clause in sql query
        if user:
            session['user_id'] = user.id
            session['role'] = user.role.lower()

            if session['role'] == 'admin':
                return redirect('/admin_dashboard')
            elif session['role'] == 'student':
                return redirect('/student_dashboard')
            elif session['role'] == 'company':
                return redirect('/company_dashboard')
        else:
            flash('Invalid username or password')
    return render_template("login.html")
                
#signup page 
@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')#from dropdown menu
        existing = Users.query.filter_by(username=username).first()
        if existing:
            flash("Username already exists")
            return redirect('/signup')
        newuser = Users(username = username, password = password, role = role)
        db.session.add(newuser)
        db.session.commit()

        if role == 'student':
            department = request.form.get('department')
            resume = request.form.get('resume') #path to resume file
            student_profile = Students(user_id = newuser.id, name = username, department = department, resume = resume)
            db.session.add(student_profile)
            db.session.commit()

        elif role == 'company':
            company_name = request.form.get('company_name')
            hr_contact = request.form.get('hr_contact')
            is_blacklisted = request.form.get('is_blacklisted')
            company_profile = Companies(user_id = newuser.id, company_name = company_name, hr_contact = hr_contact, status = False, is_blacklisted = False)
            db.session.add(company_profile)
            db.session.commit()
            
        flash('Signup successful, redirecting to login page...')
        return redirect('/login')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect('/login')



#_____________________________________________________________________________________________________________
#admin dashboard
@app.route('/admin_dashboard', methods = ['GET', 'POST'])
def admin_dashboard():
    if'user_id' not in session or session['role']!='admin':
        flash('Access not allowed. Contact admin.')
        return redirect('/login')
    
    student_search = request.args.get('student_search')
    company_search = request.args.get('company_search')

    if student_search:
        students = Students.query.filter(Students.name.ilike(f"%{student_search}%") | Students.id.ilike(f"%{student_search}%")).all()
    else:
        students = Students.query.all()

    
    if company_search:
        companies = Companies.query.filter(Companies.company_name.ilike(f"%{company_search}%")).all()
    else:
        companies = Companies.query.all()

    applications = Applications.query.all()
    drives = Drives.query.all()
    total_drives = len(drives)
    total_application = len(applications)
    total_companies = len(companies)
    total_students = len(students)
    return render_template('admin_dashboard.html',
                            companies = companies, students = students, drives = drives, applications = applications, total_companies = total_companies, total_students = total_students
                           , total_application = total_application, total_drives = total_drives)

#company approval, rejection and blacklisting    
@app.route('/admin/approve_company/<int:company_id>', methods = ['POST'])
def approve_company(company_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access not allowed. Contact admin.')
        return redirect('/login')
    company = Companies.query.get(company_id)
    if company:
        company.status = True
        db.session.commit()
        flash('Company approved successfully')
    else:
        flash('Company not found')
    return redirect('/admin_dashboard')

#reject company
@app.route('/admin/reject_company/<int:company_id>', methods = ['POST'])
def reject_company(company_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access not allowed. Contact admin.')
        return redirect('/login')
    company = Companies.query.get(company_id)
    if company:
        company.status = False
        db.session.commit()
        flash('Company rejected successfully')
    else:
        flash('Company not found')
    return redirect('/admin_dashboard')

#blacklist company
@app.route('/admin/blacklist_company/<int:company_id>', methods = ['POST'])
def blacklist_company(company_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access not allowed. Contact admin.')
        return redirect('/login')
    company = Companies.query.get(company_id)
    if company:
        company.is_blacklisted = True
        db.session.commit()
        flash('Company blacklisted successfully')
    else:
        flash('Company not found')
    return redirect('/admin_dashboard')


#student blacklisting
@app.route('/admin/blacklist_student/<int:student_id>', methods = ['POST'])
def blacklist_student(student_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access not allowed. Contact admin.')
        return redirect('/login')
    student = Students.query.get(student_id)
    if student:
        student.is_blacklisted = True
        db.session.commit()
        flash('Student blacklisted successfully')
    else:
        flash('Student not found')
    return redirect('/admin_dashboard')

#view drives 
@app.route('/view_drives', methods = ['GET'])
def view_drives():
    if 'user_id' not in session or session['role']!='admin':
        flash('Access not allowed, contact admin.')
        return redirect('/login')
    drives = Drives.query.all()
    return render_template('view_drives.html', drives = drives)

#complete mark drives 
@app.route('/admin/mark_as_complete/<int:drive_id>', methods = ['POST'])
def mark_as_complete(drive_id):
    if 'user_id' not in session or session['role']!='admin':
        flash('Access not allowed, contact admin.')
        return redirect('/login')
    drive = Drives.query.get(drive_id)
    if drive:
        drive.status = True
        db.session.commit()
        flash("Drive marked as complete.")
    return redirect('/admin_dashboard')

#reject drives 
@app.route('/admin/reject_drive/<int:drive_id>', methods=['POST'])
def reject_drive(drive_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash("Access not allowed.")
        return redirect('/login')
    
    drive = Drives.query.get(drive_id)
    if drive:
        drive.is_rejected = True
        db.session.commit()
        flash("Drive rejected successfully")
    else:
        flash("Drive not found")
    return redirect('/admin_dashboard')


#________________________________________________________________________________________________________________
#company dashboard 

@app.route('/company_dashboard', methods = ['POST', 'GET'])
def company_dashboard():
    if 'user_id' not in session or session['role']!='company':
        flash('Access not allowed, contact admin.')
        return redirect('/login')
    company = Companies.query.filter_by(user_id = session['user_id']).first()
    if company.is_blacklisted:
        flash("Your company has been blacklisted by admin.")
        return redirect('/login')

    if not company:
        flash("Company profile not found. Please complete signup again.")
        return redirect('/login')
    drives = Drives.query.filter_by(company_id = company.id).all()
    return render_template('company_dashboard.html',drives = drives, company = company)

#create drives 
@app.route('/create_drive', methods=['GET','POST'])
def create_drive():
    company = Companies.query.filter_by(user_id = session['user_id']).first()
    
    if not company.status:
        flash("Admin approval pending...")
        return redirect('/company_dashboard')

    if request.method == 'POST':
        drive_name = request.form.get('drive_name')
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        salary = request.form.get('salary')
        location = request.form.get('location')
        deadline = request.form.get('deadline')
        deadline = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
        company = Companies.query.filter_by(user_id=session['user_id']).first()
        drive = Drives( company_id=company.id,
                                drive_name=drive_name,
                                job_title=job_title,
                                job_description=job_description,
                                salary=salary,
                                location=location,
                                deadline=deadline)
        db.session.add(drive)
        db.session.commit()
        return redirect('/company_dashboard')
    return render_template("create_drive.html")

@app.route('/edit_drive/<int:drive_id>', methods = ['POST', 'GET'])
def edit_drive(drive_id):
    drive = Drives.query.filter_by(id = drive_id).first()
    if not drive:
        return "Drive not found"
    
    drive.drive_name = request.form.get('drive_name')
    drive.job_title=request.form.get('job_title')
    drive.job_description=request.form.get('job_description')
    drive.salary=request.form.get('salary')
    drive.location=request.form.get('location')
    drive.deadline=datetime.strptime(request.form.get('deadline'), '%Y-%m-%dT%H:%M')
    db.session.commit()
    return redirect('/company_dashboard')

@app.route('/company/view_applications/<int:drive_id>', methods = ['GET', 'POST'])
def view_applications(drive_id):
    if 'user_id' not in session or session['role']!='company':
        return redirect('/login')
    applications = Applications.query.filter_by(drive_id=drive_id).all()
    return render_template('applications.html', applications=applications)



@app.route('/company/update_application/<int:app_id>/<status>',methods = ['POST', 'GET'])
def update_application(app_id, status):
    application = Applications.query.filter_by(id = app_id).first()
    if not application:
        return "Application not found"
    application.status = status
    db.session.commit()
    return redirect(request.referrer)



#__________________________________________________________________________________________________________________________

@app.route('/student_dashboard', methods=['POST', 'GET'])
def student_dashboard():
    if 'user_id' not in session or session['role']!='student':
        return redirect('/login')
    
    student = Students.query.filter_by(user_id=session['user_id']).first()
    if not student:
        flash("Student profile not found.")
        return redirect('/login')

    if student.is_blacklisted:
        flash("You are blacklisted and cannot access the portal.")
        return redirect('/login')
    
    drives = Drives.query.filter_by(status=False, is_rejected=False).all()
    applications = Applications.query.filter_by(student_id=student.id).all()
    return render_template('student_dashboard.html', drives=drives, applications=applications, student=student)



@app.route('/apply/<int:drive_id>', methods=['POST'])
def apply(drive_id):
    if 'user_id' not in session or session['role']!='student':
        return redirect('/login')
 
    student = Students.query.filter_by(user_id=session['user_id']).first()

    if student.is_blacklisted:
        flash("You are blacklisted and cannot access the portal.")
        return redirect('/login')

    existing = Applications.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    if existing:
        flash("Already applied")
        return redirect('/student_dashboard')
    
    application = Applications(student_id = student.id, drive_id = drive_id, date = datetime.now())
    db.session.add(application)
    db.session.commit()
    flash("Application submitted")
    return redirect('/student_dashboard')

@app.route('/student/edit_profile/<int:id>', methods=['GET','POST'])
def edit_profile(id):
    if 'user_id' not in session or session['role'] != 'student':
        return redirect('/login')
    student = Students.query.filter_by(user_id=id).first()
    if not student:
        return "Student record not found"
    if request.method == 'POST':
        student.name = request.form.get('name')
        student.department = request.form.get('department')
        student.resume = request.form.get('resume')
        db.session.commit()
        flash("Profile updated successfully")
        return redirect('/student_dashboard')
    return render_template('edit_profile.html', student=student)



if __name__=="__main__":
    app.run(debug=True)