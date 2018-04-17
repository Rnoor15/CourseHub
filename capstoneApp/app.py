from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/rifatnoor/Desktop/capstoneApp/courseHub.db'
app.config['SECRET_KEY'] = 'lol'

db = SQLAlchemy(app)

class user(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(15))
    lastname = db.Column(db.String(15))
    email = db.Column(db.String(50), unique = True)
    password = db.Column(db.String(50))


class RegisterForm(Form):
    firstname = StringField('Enter First Name', [validators.InputRequired('Please enter a First Name')])
    lastname = StringField('Enter Last Name', [validators.InputRequired('Please enter a First Name')])
    email = StringField('Enter Email', [validators.InputRequired('Please enter a First Name')])
    password = PasswordField('Enter Password', [
        validators.InputRequired('Please enter a password'),
        validators.EqualTo('confirm', message = 'Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

class PostForm(Form):
    title = StringField('Title', [validators.InputRequired('Please enter a title')])
    body = TextAreaField('Enter text', [validators.InputRequired('Please enter a description')])

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        hashed_password = sha256_crypt.encrypt(str(form.password.data))

        new_user = user(firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1> Hello {} {}'.format(form.firstname.data, form.lastname.data)

    return render_template('register.html', form=form)

@app.route('/post', methods = ['GET', 'POST'])
def post():

    form = PostForm(request.form)

    return render_template('post.html', form=form)


if __name__ == '__main__':
   app.run(debug=True)
