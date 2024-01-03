from flask import Flask, render_template,flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

#create a Flask Instance
app = Flask(__name__)
#app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SECRET_KEY'] = "my super secret key is here"

#Create Form Class
class NamerForm(FlaskForm):
   name= StringField ("Enter your Name here", validators=[DataRequired()])
   submit= SubmitField("Submit")


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
