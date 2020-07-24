from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from . import app
from app import db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm
from app.models import User, Post
from datetime import datetime


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('You post is alive!', 'success')
        return redirect(url_for('home'))

    # the user must see followed user posts
    #posts = current_user.followed_posts().all()
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('home', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('home', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title="Microblog", posts=posts.items, form=form, 
                            next_url=next_url, prev_url=prev_url
            )


@app.route('/login', methods=['POST', 'GET'])
def login():
    # instantiate form from LoginFrom created earlier
    form = LoginForm()
    if form.validate_on_submit():
        # check if user authentication is valid
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid user credentials', 'danger')
            return redirect(url_for('login'))
        # authentication is successful
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')

        flash('Welcome again', 'success')
        return redirect(next_page)

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations you are now a member of our family', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', form=form, title='Register')


@app.route('/home/user/<username>')
@login_required
def user(username):
    u = User.query.filter_by(username=username).first_or_404()
    # get qeury param
    page = request.args.get('page', 1, type=int)
    # paginate posts
    posts = u.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
        )
    next_url = url_for('user', username=u.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=u.username, page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', title=username, posts=posts.items, user=u,
            next_url=next_url, prev_url=prev_url, form=form
        )


@login_required
@app.route('/home/edit', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your information have been changed', 'success')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit profile', form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username), 'danger')
            return redirect(url_for('home'))
        if user == current_user:
            flash('You cannot follow yourself!', 'danger')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username), 'success')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('home'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username), 'danger')
            return redirect(url_for('home'))
        if user == current_user:
            flash('You cannot unfollow yourself!', 'danger')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username), 'secondary')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('home'))


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )

    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title='Explore', posts=posts.items,
            next_url=next_url, prev_url=prev_url
        )


# Begin of my modifications
@app.route('/home/post/delete/<id>')
@login_required
def delete_post(id):
    post = Post.query.get(id)
    if post:
        db.session.delete(post)
        db.session.commit()
        flash('Your post is deleted', 'success')
    return redirect(url_for('home'))
# End of my modifications
