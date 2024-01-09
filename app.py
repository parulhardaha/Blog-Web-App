from flask import Flask, render_template,flash,request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea

#create a Flask Instance
app = Flask(__name__)

#Add sql database 
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Mysql  database 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/our_users'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'


#Secret key
#app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'~
app.config['SECRET_KEY'] = "my super secret key is here"

#Initalize The Databse
db = SQLAlchemy(app)
migrate=Migrate(app,db)
#app.app_context().push()

# Create a Blog Post Model
class Posts(db.Model):
  id= db.Column(db.Integer,primary_key=True)
  title=db.Column(db.String(200))
  content=db.Column(db.Text)
  author=db.Column(db.String(200))
  date_added=db.Column(db.DateTime,default=datetime.utcnow)
  slug=db.Column(db.String(200))

#Create Posts Form
class PostForm(FlaskForm):
  title=StringField("Title",validators=[DataRequired()])
  content=StringField("Content",validators=[DataRequired()],widget=TextArea())
  author=StringField("Author",validators=[DataRequired()])
  slug=StringField("Slug",validators=[DataRequired()])
  submit=SubmitField("Submit")

#Add pOst page
@app.route('/add-post', methods=['GET','POST']) 
def add_post():
  form=PostForm()

  if form.validate_on_submit():
    post=Posts(title=form.title.data,content=form.content.data,author=form.author.data,slug=form.slug.data)
    #Clear data
    form.title.data=''
    form.content.data=''
    form.author.data=''
    form.slug.data=''

    #Add data to database
    db.session.add(post)
    db.session.commit()

    flash("Blog Post Submitted Successfully!")

    #Redirect to the webpage
  return render_template("add_post.html",form=form)

#json thing
@app.route('/date')
def get_current_date():
  return{"Date" : date.today()}
  
#Crete Model
class Users(db.Model):
  id= db.Column(db.Integer,primary_key=True)
  name=db.Column(db.String(100),nullable=False)
  email=db.Column(db.String(100),nullable=False,unique=True)
  favorite_Colour=db.Column(db.String(100))
  date_added=db.Column(db.DateTime,default=datetime.utcnow)
  #Password stuff
  password_hash=db.Column(db.String(120))

  @property
  def password(self):
    raise AttributeError('Password is not Readable!')
  
  @password.setter
  def password(self,password):
    self.password_hash=generate_password_hash(password)
  
  def verify_password(self,password):
    return check_password_hash(self.password_hash,password)
  
  #Create A String
  def __repr__(self):
    return '<Name %r>' % self.name
  
@app.route('/delete/<int:id>')  
def  delete(id):
  user_to_delete=Users.query.get_or_404(id)
  name=None
  form=UserForm()
   
  try:
    db.session.delete(user_to_delete)
    db.session.commit()
    flash("User Deleted Successfully!")
    our_users=Users.query.order_by(Users.date_added)   
    return render_template("add_user.html",form=form,name=name,our_users=our_users)
  except:
    flash("There is an Error!!")
    our_users=Users.query.order_by(Users.date_added)   
    return render_template("add_user.html",form=form,name=name,our_users=our_users)

#Create User Class
class UserForm(FlaskForm):
   name= StringField ("Enter your Name here", validators=[DataRequired()])
   email= StringField ("Email", validators=[DataRequired()])
   favorite_Colour=StringField("Favorite Colour")
   password_hash=PasswordField('Password', validators=[DataRequired(),EqualTo('password_hash2',message="Passowrds mush match!")])
   password_hash2=PasswordField('Confirm Password',validators=[DataRequired()])
   submit= SubmitField("Submit") 

#Update Database Record
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
  form=UserForm()
  name_to_update=Users.query.get_or_404(id)
  if request.method=='POST':
    name_to_update.name=request.form['name']
    name_to_update.email=request.form['email']
    name_to_update.favorite_Colour=request.form['favorite_Colour']
    try:
      db.session.commit()
      flash("User Updated Successfully!")
      return render_template("update.html",form=form,name_to_update=name_to_update,id=id)
    except:
      flash("Error!!..Try again!!")
      return render_template("update.html",form=form,name_to_update=name_to_update)
  else:
     return render_template("update.html",form=form,name_to_update=name_to_update,id=id)

#Create Form Class-Passwd
class PasswordForm(FlaskForm):
   email= StringField ("Enter your Email", validators=[DataRequired()])
   password_hash= PasswordField ("Enter your Password", validators=[DataRequired()])
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
       #Hashed Passwd
       hashed_pw=generate_password_hash(form.password_hash.data,"sha256")
       user=Users(name=form.name.data,email=form.email.data,favorite_Colour=form.favorite_Colour.data,password_hash=hashed_pw)
       db.session.add(user)
       db.session.commit()
     name=form.name.data   
     form.name.data=''
     form.email.data=''
     form.favorite_Colour.data=''
     form.password_hash.data=''
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

#Create Password Page
@app.route('/test_pw',methods=['GET','POST'])
def test_pw():
  email=None
  password=None
  pw_to_check=None
  passed=None
  form=PasswordForm()

  #Validate Form
  if form.validate_on_submit():
     email=form.email.data
     password=form.password_hash.data
     form.email.data=''
     form.password_hash.data=''

     #Lool up user by Email address
     pw_to_check=Users.query.filter_by(email=email).first()

     #Check hash pwwsd
     passed=check_password_hash(pw_to_check.password_hash,password)


  return render_template("test_pw.html",email=email,password=password,pw_to_check=pw_to_check,passed=passed,form=form)

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

@app.route('/reset_table')  
def reset_table():
  try:
    db.drop_all()
    db.create_all()
    flash("Reset databases Successfully!")
  except Exception as e:
    flash("Some error occurred while resetting databases")
  return render_template("200.html")
