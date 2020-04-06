import os
import secrets
from time import localtime, strftime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt, socketio
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ProjectForm, UpdateProjectForm, CardForm
from app.models import User, Project, Card
from flask_login import login_user, logout_user, current_user, login_required
from flask_socketio import send, emit, join_room, leave_room

# Pre-defined chat rooms
ROOMS = ["general", "design", "prototype", "problems"]

# ROUTES
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}. You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please verify that email and password are spelled correctly.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated.', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post')

@app.route("/myprojects/new", methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        project = Project(title=form.title.data, description=form.description.data, author=current_user)
        db.session.add(project)
        db.session.commit()
        flash('You have successfully created a new project', 'success')
        return redirect(url_for('user_projects', username = current_user.username))
    return render_template('create_project.html', title='New Project', form=form, legend = 'New Project')

@app.route("/user/<string:username>/myprojects")
@login_required
def user_projects(username):
    user = User.query.filter_by(username=username).first_or_404()
    projects = Project.query.filter_by(author=user)
    return render_template('myprojects.html', projects=projects, user=current_user)

@app.route("/myprojects/<int:project_id>")
def project(project_id):
    project = Project.query.get_or_404(project_id)
    backlogs = Card.query.filter_by(status = 'backlog', author=project).all()
    incompletes = Card.query.filter_by(status = 'incomplete', author=project).all()
    completes = Card.query.filter_by(status = 'complete', author=project).all()
    return render_template('project.html', title=project.title, project=project, backlogs = backlogs, incompletes = incompletes, completes = completes)

@app.route("/myprojects/<int:project_id>/update", methods=['GET', 'POST'])
@login_required
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.author != current_user:
        abort(403)
    form = UpdateProjectForm()
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        db.session.commit()
        flash('Your project has been successfully updated.', 'success')
        return redirect(url_for('project',project_id=project.id))
    elif request.method == 'GET':
        form.title.data=project.title
        form.description.data=project.description
    return render_template('create_project.html', title='Update Project', form=form, legend = 'Update Project')

@app.route("/myprojects/<int:project_id>/delete", methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.author != current_user:
        abort(403)
    db.session.delete(project)
    db.session.commit()
    flash('Your project has been successfully deleted.', 'success')
    return redirect(url_for('user_projects', username = current_user.username))

@app.route("/myprojects/<int:project_id>/cards/new", methods=['GET', 'POST'])
@login_required
def create_card(project_id):
    project = Project.query.get_or_404(project_id)
    backlogs = Card.query.filter_by(status = 'backlog', author=project).all()
    form = CardForm()
    if form.validate_on_submit():
        card = Card(title=form.title.data, description=form.description.data, author=project)
        db.session.add(card)
        db.session.commit()
        flash('You have successfully created a new card', 'success')
        return render_template('project.html', title=project.title, project=project, backlogs = backlogs)
    return render_template('create_card.html', title='Create Card', form=form, legend = 'Create Card')

@app.route("/chat", methods=['GET', 'POST'])
def chat():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('login'))
    return render_template('chat.html', username = current_user.username, rooms = ROOMS)

@socketio.on('message')
def message(data):
    print(f"\n\n{data}\n\n")
    send({'msg': data['msg'], 'username': data['username'], 'time_stamp': strftime('%b-%d %I:%M%p', localtime())}, room=data['room'])

@socketio.on('join')
def join(data):
    join_room(data['room'])
    send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room=data['room'])

@socketio.on('leave')
def leave(data):
    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room=data['room'])