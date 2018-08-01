from flask import Flask,url_for,request,render_template,g,session,flash,redirect
from . import app
from config import Config
from app import app,db,login
from .form import LoginForm,EditProfileForm,RegisterForm
from .models import User
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts =[
        {'author':{'name':'John'},
        'body':'this is the first time using machenical keyboard,the edit feeling is awesome!'
        },
        {
        'author':{'name':'Henry'},
        'body':'I don`t know why just geting to start to use it'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts
        )


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

#  登录视图函数  #


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(u'Invalid username or password', 'error')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.name)
    if form.validate_on_submit():
        current_user.name = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(u'Your changes have been saved.', 'warning')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

#  登录后视图函数  #


# @oid.after_login
# def after_login():
# 	if resp.email is None or resp.email == '':
# 		flash('Invalid login. Please try again.')
# 		return redirect(url_for('login'))
# 	user = User.query.filter_by(email.resp.email).first()
# 	if user is None:
# 		name = resp.name
# 		if name is None or name == '':
# 			user = models.User(name = name,email = resp.email)
# 			db.session.add(user)
# 			db.session.commit()
# 	remember_me = False
# 	if 'remember_me' in session:
# 		remember_me = sessionp['remember_me']
# 		session.pop('remember_me',None)
# 	login_user(user, remember = remember_me)
# 	return redirect(url_for('hello'))

#  登出视图函数  #


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<name>')
@login_required
def user(name):
    user = User.query.filter_by(name=name).first_or_404()  #
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'authot': user, 'body': 'Test post #1'}
    ]
    return render_template('user.html', user = user, post = posts)


@app.route('/register', methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
            return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(name=form.username.data,email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(u'Congratuations,you are registered successfully', 'warning')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/follow')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))