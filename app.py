from flask import Flask, render_template,flash,request,redirect,url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, login_required,LoginManager,current_user,logout_user
from flask_ckeditor import CKEditor
from flask_ckeditor import CKEditorField

#create a Flask Instance
app = Flask(__name__)
# Add ckeditor
ckeditor=CKEditor(app)

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

#flask_login stuff
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
  return Users.query.get(int(user_id))



#Create seacrh form
class SearchForm(FlaskForm):
  searched=StringField("searched",validators=[DataRequired()])
  submit=SubmitField("Submit")

#Pass stuff for Navbar
@app.context_processor
def base():
  form=SearchForm()
  return dict(form=form)

#Create admin page
@app.route('/admin')
@login_required
def admin():
  id=current_user.id
  if id==13:
    return render_template("admin.html")
  else:
    flash("Sorry,You must be Admin to access this Page!!")
    return redirect(url_for('dash'))


#Create search fun
@app.route('/search',methods=["POST"])
def search():
  form=SearchForm()
  #print("searched", form.searched.data)
  if form.validate_on_submit():
    post.searched=form.searched.data
    return render_template("search.html",form=form,searched=post.searched)
  #return render_template("200.html")



#Create login form
class LoginForm(FlaskForm):
  username=StringField("UserName",validators=[DataRequired()])
  password=PasswordField("Password",validators=[DataRequired()])
  submit=SubmitField("Submit")
 
#Create Login Page
@app.route('/login',methods=['POST','GET'])
def login():
  form=LoginForm()
  if form.validate_on_submit():
     user=Users.query.filter_by(username=form.username.data).first()
     if user:
        #check hash
        if check_password_hash(user.password_hash,form.password.data):
          login_user(user)
          flash("Login Successfull!!")
          return redirect(url_for('dash'))
        else:
          flash("Wrong Passowrd - Tyr again!!")
     else:
      flash("User does not exist - try again!!")     
  
  return render_template("login.html",form=form)

#Create logout Page
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
  logout_user()
  flash("You have been Logged out!! ")
  return redirect(url_for('login'))

#Create Dashboard Page
@app.route('/dash',methods=['POST','GET'])
@login_required
def dash():
  return render_template("dash.html")


# Create a Blog Post Model
class Posts(db.Model):
  id= db.Column(db.Integer,primary_key=True)
  title=db.Column(db.String(200))
  content=db.Column(db.Text)
  #author=db.Column(db.String(200))
  date_added=db.Column(db.DateTime,default=datetime.utcnow)
  slug=db.Column(db.String(200))
  # Foreign key to link Users()->182
  poster_id=db.Column(db.Integer, db.ForeignKey('users.id'))

#Create Posts Form
class PostForm(FlaskForm):
  title=StringField("Title",validators=[DataRequired()])
  #content=StringField("Content",validators=[DataRequired()],widget=TextArea())
  content = CKEditorField('Content')
  author=StringField("Author")
  slug=StringField("Slug",validators=[DataRequired()])
  submit=SubmitField("Submit")

#
@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
  post_to_delete=Posts.query.get_or_404(id)
  id=current_user.id 
  if id==post_to_delete.poster.id:
    try:
       db.session.delete(post_to_delete)
       db.session.commit()
       flash("Blog Post Was Deleted Successfully!")
       #Grab all the posts form database
       posts=Posts.query.order_by(Posts.date_added)
       return render_template("posts.html",posts=posts)
    except:  
        flash("Whoops! There was a problem deleting this Post! ")
        #Grab all the posts form database
        posts=Posts.query.order_by(Posts.date_added)
        return render_template("posts.html",posts=posts)
  else:
    flash("You aren't authorized to Delete that Post!")  
    posts=Posts.query.order_by(Posts.date_added)
    return render_template("posts.html",posts=posts)

#Add posts page
@app.route('/posts')
def posts():
  #Grab all the posts form database
  posts=Posts.query.order_by(Posts.date_added)
  return render_template("posts.html",posts=posts)
  
#A particular Post page
@app.route('/posts/<int:id>')
def post(id):
  post=Posts.query.get_or_404(id)
  return render_template("post.html",post=post)

#Edit post page
@app.route('/posts/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit_post(id):
  post=Posts.query.get_or_404(id)
  form=PostForm()
  if form.validate_on_submit():
    post.title=form.title.data
    #post.author=form.author.data
    post.slug=form.slug.data
    post.content=form.content.data
    #Update Database
    db.session.add(post)
    db.session.commit()
    flash("Post Has Been Updated!")
    return redirect(url_for('post',id=post.id))
  
  if current_user.id==post.poster.id: 
    form.title.data=post.title
    #form.author.data=post.author
    form.slug.data=post.slug
    form.content.data=post.content
    return render_template('edit_post.html',form=form)
  else:
    flash("You are not authorizes to Edit this Post!")
    posts=Posts.query.order_by(Posts.date_added)
    return render_template("posts.html",posts=posts)
  

#Add pOst page
@app.route('/add-post', methods=['GET','POST']) 
@login_required
def add_post():
  form=PostForm()

  if form.validate_on_submit():
    poster=current_user.id
    post=Posts(title=form.title.data,content=form.content.data,poster_id=poster,slug=form.slug.data)
    #Clear data
    form.title.data=''
    form.content.data=''
    #form.author.data=''
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
class Users(db.Model,UserMixin):
  id= db.Column(db.Integer,primary_key=True)
  username=db.Column(db.String(20),nullable=False,unique=True)
  name=db.Column(db.String(100),nullable=False)
  email=db.Column(db.String(100),nullable=False,unique=True)
  favorite_Colour=db.Column(db.String(100))
  date_added=db.Column(db.DateTime,default=datetime.utcnow)
  #Password stuff
  password_hash=db.Column(db.String(120))
  #User can have many post(one to many)->90
  posts=db.relationship('Posts',backref='poster')

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
   username= StringField ("Enter your UserName", validators=[DataRequired()])
   email= StringField ("Email", validators=[DataRequired()])
   favorite_Colour=StringField("Favorite Colour")
   password_hash=PasswordField('Password', validators=[DataRequired(),EqualTo('password_hash2',message="Passowrds mush match!")])
   password_hash2=PasswordField('Confirm Password',validators=[DataRequired()])
   submit= SubmitField("Submit") 

#Update Database Record
@app.route('/update/<int:id>', methods=['GET','POST'])
@login_required
def update(id):
  form=UserForm()
  name_to_update=Users.query.get_or_404(id)
  if request.method=='POST':
    name_to_update.name=request.form['name']
    name_to_update.email=request.form['email']
    name_to_update.favorite_Colour=request.form['favorite_Colour']
    name_to_update.username=request.form['username']
    try:
      db.session.commit()
      flash("User Updated Successfully!")
      return render_template("dash.html",form=form,name_to_update=name_to_update,id=id)
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
       user=Users(name=form.name.data,username=form.username.data,email=form.email.data,favorite_Colour=form.favorite_Colour.data,password_hash=hashed_pw)
       db.session.add(user)
       db.session.commit()
     name=form.name.data   
     form.name.data=''
     form.username.data=''
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
