from flask import Flask, redirect, render_template,request, session, url_for #session is a dictionary maintained by flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
app.secret_key = 'shraddha' #used to encrypt the session data
db=SQLAlchemy() 
db.init_app(app) 

class Student(db.Model): 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Boolean, default=True, nullable = False) #to check if user is logged in or not

with app.app_context(): 
    db.create_all()     

@app.route("/", methods = ['GET', 'POST'])
def home():
    return render_template("index.html")

#_________LOGIN PAGE______________

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('username')
        pwd = request.form.get('password')
        user = Student.query.filter_by(name=name).first() #filter_by used in place for where clause in sql query
        if user:
            if user.password == pwd:
                session['user_id'] = user.id
                return redirect("/placement_dashboard")
            else:
                return "Incorrect password"

        else:
            return "User does not exist"
    else:
        return render_template("login.html")

#_________SIGNUP PAGE______________

@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('username')
        pwd = request.form.get('password')
        user = Student(name=name, password=pwd)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    else:
        return render_template("signup.html")

#_________USER DASHBOARD________________

@app.route("/placement_dashboard", methods = ['GET', 'POST'])
def placement_dashboard():
    id = session['user_id']
    user = Student.query.filter_by(id=id).first()
    username = user.name
    return render_template("placement_dashboard.html", user_name = username)

if __name__=="__main__":
    app.run(debug=True)