# This is where all the routes are defined for our API
# It is mostly based on our design document.

import os
import secrets
from time import localtime, strftime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt, socketio
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ProjectForm, UpdateProjectForm, CardForm, InviteForm
from app.models import User, Project, Card, History, Sprint
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
    # Check if a valid user is logged in, if one is alreayd logged in, registration form shouldn't be able to be accessed
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()

    # After it goes into register html and the user has put in their info, this code happens if everything is ok
    if form.validate_on_submit():
        # for security reasons, I hash the password before putting it into the database, so you cannot get people's passwords directly through the database
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        #Add a user to our User database table specified in models.py with the information that we passed in through the registration form which was rendered with register.html
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)

        #When changing things in the database (add, update, delete), you need to commit it
        db.session.add(user)
        db.session.commit()

        #Flash just gives the user quick warnings. Once they refresh, it disappears. It is a one-time sort of thing.
        flash(f'Account created for {form.username.data}. You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    # If logged in, should redirect to home instead
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    #if not logged in, sees the login form
    form = LoginForm()
    if form.validate_on_submit():
        #I am looking through the database for a user with this email
        #Once I get it, I check the password with the password entered to verify that the user can log in if it matches
        #Bcrypt just checks the hash of what we entered to the already hashed password in the database
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            # this is if someone accesses a page that they need to be logged in to access
            # it will redirect them to what they were initially wanting to go to after they log in
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

    # Here I am formatting the pictures to save space on the server
    # Once a user cahnges their profile picture,
    # I modify it so that is it a 125x125 at max picture.

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
# this login handler is from flask-login. Basically it just checks if you have been logged in. Flask-login also gives me access to who the current_user is and how to log people out
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

# notice here that the route has variables in it, identified by <type:name> and passed into from the HTML. This is because my projects is specific to a user
# By having it in the route, I can use it to query for the user and therefore I can get their projects
# This is not terribly secure as theoretically the way I have it, anyone with this url can access it even if they are not the person
# Currently, it does not verify that you must be the person to access it.
@app.route("/user/<string:username>/myprojects/new", methods=['GET', 'POST'])
@login_required
# In the method, I have to actually pass in the username that is going to be used in the route
def create_project(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = ProjectForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        project = Project(title=form.title.data, description=form.description.data, )
        db.session.add(project)
        db.session.commit()

        # I am using advantage of the fact that projects and usesrs are a many-to-many relationship
        # So here I have to the project creator as a user that is part of this particular project
        # Further down, I do the same thing when I invite people
        # This is so we can quickly gather who is part of a project
        # This is the same logic as with a youtube channel and people subscribed to it

        project.users_in.append(user)
        db.session.commit()
        flash('You have successfully created a new project', 'success')
        return redirect(url_for('user_projects', username = current_user.username))
    return render_template('create_project.html', title='New Project', form=form, legend = 'New Project')

@app.route("/user/<string:username>/myprojects")
@login_required
def user_projects(username):
    user = User.query.filter_by(username=username).first_or_404()
    projects = user.projects_part_of

    return render_template('myprojects.html', projects=projects, user=current_user)

@app.route("/user/<string:username>/myprojects/project/<int:project_id>")
@login_required
def project(project_id,username,methods=['GET', 'POST']):
    # I am getting the particular project that the user has clicked on to go to using the project ID that is being passed into it
    # I then comunicate with the db and get all the users that have a relationship with this project ONLY and assign them into members
    # If the user who is trying to connect to the page is not part of it, they will receive a 403 page error telling them they
    # do not have permission to view this page
    project = Project.query.get_or_404(project_id)
    members = project.users_in
    if not members:
       abort(403)

    # this part is me making room for passing in backlogs, todos, and done cards
    # this part needs work for sure
    # basically, I'm querying the db via one of the properties - status
    # and then assigning everything it gets back into a variable that I pass into the project.html template
    backlogs = Card.query.filter_by(status = 'backlog', author=project).all()
    incompletes = Card.query.filter_by(status = 'incomplete', author=project).all()
    completes = Card.query.filter_by(status = 'complete', author=project).all()
    print(project.id)
    print(completes) #console logging to ensure info is being obtained
    print(incompletes)
    sprints = Sprint.query.filter_by(project_id=project.id).all()
    print(sprints)

    # here I am getting all the users involved in this project
    # remember that they are being stored via user_id since this doesn't change even if a person changes their email, username, etc.
    # But because this is how we are storing it, we need to get the actual user associated with that project so that
    # we can get info of that user to display such as their picture, name, maybe email, etc.
    usernames = []
    for var in members:
        user= User.query.get(var.id)
        usernames.append(user)

    return render_template('project.html', title=project.title, project=project, backlogs = backlogs, incompletes = incompletes, completes = completes, members=members, usernames = usernames,username = current_user.username, rooms = ROOMS, sprints=sprints)

@app.route("/user/<string:username>/myprojects/project/<int:project_id>/update", methods=['GET', 'POST'])
@login_required
def update_project(project_id, username):
    project = Project.query.get_or_404(project_id)
    form = UpdateProjectForm()
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        db.session.commit()
        flash('Your project has been successfully updated.', 'success')
        return redirect(url_for('project',project_id=project.id, username=current_user.username))
    elif request.method == 'GET':
        form.title.data=project.title
        form.description.data=project.description
    return render_template('create_project.html', title='Update Project', form=form, legend = 'Update Project')

@app.route("/user/<string:username>/myprojects/project/<int:project_id>/delete", methods=['POST'])
@login_required
def delete_project(project_id, username):
    project = Project.query.get_or_404(project_id)
    project.users_in = []
    db.session.commit()
    db.session.delete(project)
    db.session.commit()
    flash('Your project has been successfully deleted.', 'success')
    return redirect(url_for('user_projects', username = current_user.username))

@app.route("/user/<string:username>/myprojects/project/<int:project_id>/cards/new", methods=['GET', 'POST'])
@login_required
def create_card(project_id, username):
    project = Project.query.get_or_404(project_id)

    # Right now, status is being set to backlog because that's where the button is that leads to this route
    backlogs = Card.query.filter_by(status = 'backlog', author=project).all()
    form = CardForm()
    if form.validate_on_submit():
        card = Card(title=form.title.data, description=form.description.data, author=project)
        db.session.add(card)
        db.session.commit()

        # We need to include this again because after creating a card we go back into the project html which will then require this info once again
        # there's 100% a better way to do this, but this is what I have

        users = project.users_in
        usernames = []
        for var in users:
            user= User.query.get(var.id)
            usernames.append(user)
        flash('You have successfully created a new card', 'success')
        backlogs = Card.query.filter_by(status = 'backlog', author=project).all()
        return render_template('project.html', title=project.title, project=project, backlogs = backlogs, usernames = usernames)
    return render_template('create_card.html', title='Create Card', form=form, legend = 'Create Card')

@app.route("/user/<string:username>/myprojects/project/<int:project_id>/cards/<int:card_id>/delete", methods=['POST'])
@login_required
def delete_card(card_id, username, project_id):
    card = Card.query.get_or_404(project_id)
    db.session.delete(card)
    db.session.commit()
    flash('Your card has been successfully deleted.', 'success')
    return render_template('create_card.html', title='Create Card', form=form, legend = 'Create Card')

@app.route("/chat", methods=['GET', 'POST'])
def chat():
    messages = History.query.all()
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('login'))
        # chat.html links with our socketio.js and chat_page.js
    return render_template('chat.html', username = current_user.username, rooms = ROOMS, messages = messages)

@app.route("/user/<string:username>/myprojects/project/<int:project_id>/invite", methods=['GET', 'POST'])
@login_required
def invite(project_id, username):
    project = Project.query.get_or_404(project_id)
    backlogs = Card.query.filter_by(status = 'backlog', author=project).all()
    incompletes = Card.query.filter_by(status = 'incomplete', author=project).all()
    completes = Card.query.filter_by(status = 'complete', author=project).all()

    form = InviteForm()
    if form.validate_on_submit():
        user_email = form.email.data
        user = User.query.filter_by(email=user_email).first_or_404()
        project.users_in.append(user)
        db.session.commit()
        users = project.users_in
        usernames = []
        for var in users:
            user= User.query.get(var.id)
            usernames.append(user)
        flash(user_email + ' has successfully been added.', 'success')
        return render_template('project.html', title=project.title, project=project, backlogs = backlogs, incompletes = incompletes, completes = completes, usernames = usernames)
    return render_template('invite.html', title='Invite a Member', form=form, legend = 'Invite a Member')


# This is the socket stuff. Honestly, I am not too familiar with this part, and can't explain it in as much detail
# I am defining methods for sending messages, joining rooms, and leaving rooms.
# I am unsure if I want to keep the join and leave methods. I don't think they're completely necessary
@socketio.on('message')
def message(data):
    print(f"\n\n{data}\n\n")

    # Currently history is only saving the message content as well as the username of who sent the message
    # I was having a little issue with storing the date and time
    # This is also only one history. Anything messages is getting stored and it is not channel specific.
    # This has yet to be modeled in models.py
    message = History(message=data['msg'], username=data['username'])
    db.session.add(message)
    db.session.commit()
    send({'msg': data['msg'], 'username': data['username'], 'time_stamp': strftime('%b-%d %I:%M%p', localtime())}, room=data['room'])

@socketio.on('join')
def join(data):
    join_room(data['room'])
    send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room=data['room'])

@socketio.on('leave')
def leave(data):
    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room=data['room'])

@socketio.on('cardDragStart')
def cardDragStart(data):
    emit('cardDragging', data, broadcast=True)

@socketio.on('cardDrop')
def cardDrop(json):
    print(json["status"])
    card_id = json["id"]
    card_id = card_id[5:len(card_id)] #cutting off the "card_"
    print(card_id)
    stmt = db.session.query(Card).get(card_id)
    stmt.sprint_id = json["newSprint"]
    stmt.status = json['status']
    if stmt.status == 'backlog':
        stmt.sprint_id = 0
    db.session.commit()
    emit('cardDrop', json, broadcast=True)