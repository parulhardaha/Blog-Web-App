from flask import Flask, render_template,flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#create a Flask Instance
app = Flask(__name__)

#Add database 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#Secret key
#app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SECRET_KEY'] = "my super secret key is here"

#Initalize The Databse
db= SQLAlchemy(app)

#Crete Model
class Users(db.Model):
  id= db.Column(db.Integer,primary_key=True)
  name=db.Column(db.String(100),nullable=False)
  email=db.Column(db.String(100),nullable=False,unique=True)
  date_added=db.Column(db.DateTime,default=datetime.utcnow)

  #Create A String
  def __repr__(self):
    return '<Name %r>' % self.name

#Create User Class
class UserForm(FlaskForm):
   name= StringField ("Enter your Name here", validators=[DataRequired()])
   email= StringField ("Email", validators=[DataRequired()])
   submit= SubmitField("Submit") 


#Create Form Class
class NamerForm(FlaskForm):
   name= StringField ("Enter your Name here", validators=[DataRequired()])
   submit= SubmitField("Submit")

#
@app.route('/user/add', methods=['GET','POST'])   
def add_user():
  name=None
  form=UserForm()
  if form.validate_on_submit():
     user=Users.query.filter_by(email=form.email.data).first()
     if user is None:
       user=Users(name=form.name.data,email=form.email.data)
       db.session.add(user)
       db.session.commit()
     name=form.name.data   
     form.name.data=''
     form.email.data=''
     flash("User Added Data Successfully!")
  our_users=Users.query.order_by(Users.date_added)   
  return render_template("add_user.html",form=form,name=name,our_users=our_users)

#ceate a Route decorator url
# http://127.0.0.1:5000/
@app.route('/')
def index():
  first_name="Parul"
  my_list=["Pizza","Burger","Pani puri",36,"Capchinno"]
  stuff=" This is <strong>This text is important!</strong> Text"
  return render_template("index.html", first_name=first_name, stuff=stuff, my_list=my_list)

#localhost:5000/user/Parul
@app.route('/user/<name>')
def user(name):
  return render_template("user.html",user_name=name)

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
  return render_template("404.html"),404

#Internal server error
@app.errorhandler(500)
def page_not_found(e):
 return render_template("500.html"),500

#Create Nmae Page
@app.route('/name',methods=['GET','POST'])
def name():
  name=None
  form=NamerForm()
  #Validate Form
  if form.validate_on_submit():
     name=form.name.data
     form.name.data=''
     flash("Form Submitted Successfully!")

  return render_template("name.html",name=name,form=form)