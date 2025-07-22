from flask import Flask,request,render_template,url_for,redirect,session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,EmailField
from wtforms.validators import DataRequired,EqualTo,Email
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#all app and db configuration
app = Flask(__name__)
app.config['SECRET_KEY']='ksdbasd26187DFAF%$gfb29'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.sqlite3'
db = SQLAlchemy(app)

###############################################################################################
#Building database models (i.e., sql tables as classes)
class User(db.Model):#Creating USer table as a db model(class)
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(40),unique=True,nullable=False)
    password = db.Column(db.String(80),nullable=False)
    posts = db.relationship('update',backref='user',lazy=True)
    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = password
    def __repr__(self):#python dunder methods
        return f"User('{self.username}','{self.email}')"

class update(db.Model):# creating a update table as a db model (class)
    id = db.Column(db.Integer,primary_key=True)
    topic = db.Column(db.String(100),nullable=False)
    content = db.Column(db.Text)
    date_completed = db.Column(db.DateTime,nullable=False,default =datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    def __repr__(self):
        return f"update('{self.topic}','{self.date_completed}')"

############################################################################################
#creating classes using Flaskform 
class LoginForm(FlaskForm):#creating a loginform templates
    email = EmailField('email',validators=[DataRequired(),Email()])
    password = PasswordField('password',validators=[DataRequired()])
    submit = SubmitField('submit')

class SignUpForm(FlaskForm):#creating a signup form template
    name = StringField('name',validators=[DataRequired()])
    email = EmailField('email',validators=[DataRequired(),Email()])
    password = PasswordField('password',validators=[DataRequired()])
    confirm_password = PasswordField('confirm_password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('submit')

###########################################################################################
#main route to index.html
@app.route("/")
def main_page():
    return render_template("index.html",title = "Progress Tracker")

#signup route uses signup class for creating form in html using jinja templates
@app.route("/sign-up",methods=['POST','GET'])
def sign_up():
    form = SignUpForm()
    if request.method == "POST" and form.validate_on_submit():
        username = form.name.data# get the username data
        email = form.email.data# get the email data
        password = form.password.data #get thr password data

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        try:
            db.session.commit()
            session['user'] = username  # Set the user in the session
            return redirect(url_for("user_page"))
        except Exception as e:
            db.session.rollback()
            return f'An error occurred: {e}'
    return render_template("signin.html", form=form)

#Login route uses Login class for creating form in html using jinja templates
@app.route("/login-page",methods=['POST','GET'])
def Login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email,password=password).first()
        if user:
            session['user'] = user.username
            return redirect(url_for('user_page'))
        else:
            return "Invalid Credentials"
    return render_template("login.html",form = form)

#user page route 
@app.route('/user-page',methods=['POST','GET'])
def user_page():
    if 'user' in session:
        username = session['user']
        return render_template("user.html", username=username)
    else:
        return redirect(url_for('login'))







if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0',port=3000)
