from datetime import datetime
from flask import url_for, request, render_template, flash, redirect
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db, login
from .form import LoginForm, EditProfileForm, RegisterForm, PostForm, ResetPasswordRequestForm
from .models import User, Post
from app.email import send_password_reset_email
from flask_babel import _, get_locale
from guess_language import guess_language
from flask import g
from app.translate import translate
from flask import jsonify


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(author=current_user, body=form.post.data, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('your post is now alive!'))
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
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    if posts.has_next:
        next_url = url_for('explore', page=posts.next_num)
    else:
        next_url = None
    if posts.has_prev:
        pre_url = url_for('explore', page=posts.prev_num)
    else:
        pre_url = None
    return render_template("index.html", title='Explore', post=posts.items,
                           next_url=next_url, pre_url=pre_url)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


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
        flash(_(u'Your changes have been saved.'), 'warning')
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
        flash(_('Congratulations,you are registered successfully'), 'warning')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


#  reset password request view funciton#


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash(_('Check your email for the instructions to reset your password'))
            return redirect(url_for('login'))
        else:
            flash(_('this email is not exist!'), 'error')
    return render_template('reset_password_request.html',
                           form=form,
                           title='Reset Password'
                           )


#  reset password view function  #


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('email/reset_password.html', form=form, user=user)


#  follow user function  #


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(name=username).first()
    if user is None:
        flash(_('User %{username} is not found.'.username.username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


#  unfollow user function  #


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


@app.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])}
                   )
