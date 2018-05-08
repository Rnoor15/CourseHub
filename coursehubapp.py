from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import sqlite3

from time import sleep

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/tingyang/Desktop/CSCI 499/CourseHub/courseHub.db'

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


students_courses = db.Table('students_courses',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('course_id', db.Integer(), db.ForeignKey('course.id'))
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    post = db.relationship('Post', backref='user', lazy='dynamic')
    comment = db.relationship('Comment', backref='user', lazy='dynamic')
    courses = db.relationship('Course', secondary=students_courses, backref=db.backref('students'), lazy='dynamic')


class Post(db.Model):
    __tablename__ = 'post'
    __searchable__ = ['title']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    post_time = db.Column(db.DateTime, default=datetime.now)
    #rating = db.Column(db.Integer, default=0)
    comment = db.relationship('Comment', backref='post', lazy='dynamic')


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    detail = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'),nullable=False)
    comment_time = db.Column(db.DateTime, default=datetime.now)


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    post = db.relationship('Post', backref='course', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.course_name)


class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    subjectname = db.Column(db.String(20), nullable=False)
    course = db.relationship('Course', backref='subject', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.subjectname)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class PostForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    description = TextAreaField('Text', validators=[InputRequired()])


class CommentForm(FlaskForm):
    detail = TextAreaField('Text', validators=[InputRequired()])

def course_search_query():
    return Course.query

class CourseSearchForm(FlaskForm):
    options = QuerySelectField(query_factory = course_search_query, allow_blank=True)

db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                session['username'] = form.username.data
                return redirect(url_for('userspage'))

        flash("Invalid username or password!")

        return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Signup sucessful!")

        return render_template('signup.html', form=form)

    return render_template('signup.html', form=form)


@app.route('/course/<course_id>', methods=['GET', 'POST'])
@login_required
def course(course_id):
    context = {
        'post': Post.query.filter(Post.course_id==course_id).order_by(Post.post_time).all()
    }

    curr_course = Course.query.filter(Course.id==course_id).first()

    return render_template('course.html',course_id=course_id, **context, course=curr_course)


@app.route('/userpage')
@login_required
def userspage():
    user = User.query.filter_by(username=session['username']).first()
    context = {
        'course': Course.query.filter(Course.students.any(id=user.id)).all()
    }
    return render_template('userspage.html', **context)


@app.route('/coursesearch', methods=['GET', 'POST'])
@login_required
def coursesearch():

    form = CourseSearchForm()

    if form.validate_on_submit():
        addtousercourse = Course(course_name ='{}'.format(form.options.data))
        course_to_add = Course.query.filter(Course.course_name == addtousercourse.course_name).first()
        user = User.query.filter_by(username=session['username']).first()
        course_to_add.students.append(user)
        db.session.commit()

        return redirect(url_for('coursesearch'))

    return render_template('coursesearch.html', form=form)

@app.route('/removecourse', methods=['GET', 'POST'])
@login_required
def removecourse():

    form = CourseSearchForm()

    if form.validate_on_submit():
        return redirect(url_for('removecourse'))

    return render_template('removecourse.html', form=form)


@app.route('/detail/<post_id>', methods=['GET', 'POST'])
def detail(post_id):
    postdetail = Post.query.filter(Post.id == post_id).first()
    return render_template('detail.html', post=postdetail)


@app.route('/comment/<post_id>', methods=['POST'])
@login_required
def comment(post_id):
    if not request.form.get('comment_detail'):
        return redirect(url_for('detail', post_id=post_id))
    detail = request.form.get('comment_detail')
    user = User.query.filter_by(username=session['username']).first()
    post = Post.query.filter(Post.id == post_id).first()
    comment = Comment(detail=detail)
    comment.post = post
    comment.user = user
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('detail', post_id=post_id))


@app.route('/post/<course_id>', methods=['GET', 'POST'])
@login_required
def post(course_id):
    form = PostForm()
    curr_course = Course.query.filter(Course.id==course_id).first()

    if form.validate_on_submit():
        user = User.query.filter_by(username=session['username']).first()
        new_post = Post(title=form.title.data, description=form.description.data, user_id=user.id, course_id=course_id)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('course', course_id=course_id))

    return render_template('post.html', form=form, course_id=course_id, course=curr_course)


@app.route('/usercenter/<username>/<tag>')
@login_required
def usercenter(username,tag):

    user = User.query.filter(User.username == username).first()
    context={
        'user':user
    }
    if tag == 'post':
        return render_template('usercenter1.html', **context)
    else:
        return render_template('usercenter2.html', **context)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)