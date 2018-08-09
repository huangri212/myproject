from datetime import datetime
from flask import url_for, request, render_template, flash, redirect
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db, login
from .form import LoginForm, EditProfileForm, RegisterForm, PostForm
from .models import User, Post


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(author=current_user, body=form.post.data)
        print (post.body)
        db.session.add(post)
        db.session.commit()
        # post = Post.query.filter_by(user_id=1).first()
        flash('your post is now alive!')
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    if posts.has_next:
        next_url = url_for('index', page=posts.next_num)
    else:
        next_url = None
    if posts.has_prev:
        pre_url = url_for('index', page=posts.prev_num)
    else:
        pre_url = None
    return render_template('index.html', title='Home Page', post=posts, form=form,
                           next_url=next_url, pre_url=pre_url)

# pagination view function#


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    post = Post.query.order_by(Post.timestamp.desc()).paginate(page,app.config('POSTS_PER_PAGE'))
    if post.has_next:
        next_url = url_for('index', page=post.next_num)
    else:
        next_url = None
    if post.has_pre:
        pre_url = url_for('index', post.pre_num)
    else:
        pre_url = None
    return render_template('index.html', title='Home Page', post=post.items, next_url=next_url, pre_url=pre_url)



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# login view function  #


@app.route('/login', methods=['GET', 'POST'])
def login():
    # type: () -> login
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


#  edit_profile view function  #


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


# logout view function  #


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<name>')
@login_required
def user(name):
    user = User.query.filter_by(name=name).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #1'}
    ]
    return render_template('user.html', user=user, post=posts)


# register view function  #


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(name=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(u'Congratulations,you are registered successfully', 'warning')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


#  follow user function  #


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(name=username).first()
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


#  follow user function  #


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(name=username).first()
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
