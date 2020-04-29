# This is where all the routes are defined for our API
# It is mostly based on our design document.

import os
import secrets
from time import localtime, strftime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt, socketio
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ProjectForm, UpdateProjectForm, CardForm, InviteForm
from app.models import User, Project, Card, Chat_History, Sprint, subs,Channel
from flask_login import login_user, logout_user, current_user, login_required
from flask_socketio import send, emit, join_room, leave_room
from datetime import datetime
from sqlalchemy import inspect
import json
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


def save_project_picture(form_picture):

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/project_pics', picture_fn)

    max_size = (900, 900)
    i = Image.open(form_picture)
    i.thumbnail(max_size)

    i.save(picture_path)

    return picture_fn

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
            picture_file = save_project_picture(form.picture.data)
            project = Project(title=form.title.data, description=form.description.data, image_file = picture_file)
            db.session.add(project)
            db.session.commit()
        else:
            project = Project(title=form.title.data, description=form.description.data)
            db.session.add(project)
            db.session.commit()

        # I am using advantage of the fact that projects and usesrs are a many-to-many relationship
        # So here I have to the project creator as a user that is part of this particular project
        # Further down, I do the same thing when I invite people
        # This is so we can quickly gather who is part of a project
        # This is the same logic as with a youtube channel and people subscribed to it

        project.users_in.append(user)
        json = {'id' : project.id,'sprint':1}
        toAdd = Sprint(project_id=json["id"], sprint_num = json["sprint"])
        db.session.add(toAdd)
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

    sprints = Sprint.query.filter_by(project_id=project.id).all()

    backlogs = Card.query.filter_by(status = 'backlog', project_id=project_id).all()
    incompletes = Card.query.filter_by(status = 'incomplete', project_id=project_id).all()
    completes = Card.query.filter_by(status = 'complete', project_id=project_id).all()
    
    usernames = []
    for var in members:
        user= User.query.get(var.id)
        usernames.append(user)

    return render_template('project.html', title=project.title, project=project, backlogs = backlogs, incompletes = incompletes,
     completes = completes, members=members, usernames = usernames,username = current_user.username, rooms = ROOMS, sprints=sprints)

@app.route("/user/<string:username>/myprojects/project/<int:project_id>/update", methods=['GET', 'POST'])
@login_required
def update_project(project_id, username):
    project = Project.query.get_or_404(project_id)
    form = UpdateProjectForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_project_picture(form.picture.data)
            project.image_file = picture_file
        project.title = form.title.data
        project.description = form.description.data
        db.session.commit()
        flash('Your project has been successfully updated.', 'success')
        socketio.emit('project_update',{'project_id':project_id,'project_title':project.title,'project_description':project.description,'project_image':project.image_file},broadcast=True)
        return redirect(url_for('project',project_id=project.id, username=current_user.username))
    elif request.method == 'GET':
        form.title.data=project.title
        form.description.data=project.description
    return render_template('create_project.html', title='Update Project', form=form, legend = 'Update Project')

@app.route("/user/<string:username>/myprojects/project/<int:project_id>/delete", methods=['POST'])
@login_required
def delete_project(project_id, username):
    for row in db.session.query(Card).filter(Card.project_id == project_id):
        db.session.delete(row)
    db.session.commit()

    for row in db.session.query(Sprint).filter(Sprint.project_id == project_id):
        db.session.delete(row)
    db.session.commit()
    
    for row in db.session.query(Chat_History).filter(Chat_History.project_id == project_id):
        db.session.delete(row)
    db.session.commit()
 
    for row in db.session.query(Channel).filter(Channel.project_id == project_id):
        db.session.delete(row)
    db.session.commit()

    subss = db.session.query(subs).filter_by(project_id=project_id)
    subss.delete(synchronize_session=False)
    db.session.commit()
    
    project = Project.query.get_or_404(project_id)
    project.users_in = []
    db.session.delete(project)
    db.session.commit()
    flash('Your project has been successfully deleted.', 'success')
    return redirect(url_for('user_projects', username = current_user.username))

@app.route("/user/<string:username>/myprojects/project/<int:project_id>/cards/new", methods=['GET', 'POST'])
@login_required
def create_card(project_id, username):
    project = Project.query.get_or_404(project_id)

    # Right now, status is being set to backlog because that's where the button is that leads to this route
    form = CardForm()
    if form.validate_on_submit():
        card = Card(title=form.title.data, description=form.description.data, author=project)
        db.session.add(card)
        db.session.commit()
        ident = card.id
        flash('You have successfully created a new card', 'success')
        socketio.emit('cardCreate', {'card_id' : ident, 'priority':'black', 'title':form.title.data, 'project_id':project_id}, broadcast = True)
        return redirect(url_for('project',project_id=project.id, username=current_user.username))

    return render_template('create_card.html', title='Create Card', form=form, legend = 'Create Card')

@app.route("/user/<string:username>/myprojects/project/<int:project_id>/invite", methods=['GET', 'POST'])
@login_required
def invite(project_id, username):
    project = Project.query.get_or_404(project_id)
    form = InviteForm()
    if form.validate_on_submit():
        user_email = form.email.data
        user = User.query.filter_by(email=user_email).first_or_404()
        subss = db.session.query(subs).filter_by(project_id=project_id, user_id= user.id).all()
        if len(subss) == 0:
            project.users_in.append(user)
            db.session.commit()
            flash(user_email + ' has successfully been added.', 'success')
            socketio.emit('listInvitedUser',{'project_id':project_id, 'username':username,'new_member_username':user.username,'new_member_photo':user.image_file},broadcast = True)
        else:
            flash(user_email + ' is already in this project', 'success')
        return redirect(url_for('project',project_id=project.id, username=current_user.username))
    return render_template('invite.html', title='Invite a Member', form=form, legend = 'Invite a Member')


# These are the socket functions for joining/leaving rooms and sending messages
@socketio.on('message')
def message(data):
    print(f"\n\n{data}\n\n")
    message = Chat_History(message=data['msg'],username = data['username'],room =data['room'], project_id = data['project_id'])
    db.session.add(message)
    db.session.commit()
    emit('message',{'msg': data['msg'], 'username': data['username'], 'time_stamp': strftime('%b-%d %I:%M%p', localtime()),'room':data['room']}, room=data['room_displayed'])
    #if(data['username'] == )
    

def myconverter(time):
    time = datetime.strftime(time,'%b-%d %I:%M%p')
    return time

@socketio.on('join')
def join(data):
    join_room(data['room'])
    messages = Chat_History.query.filter_by(project_id = data['project_id'], room = data['room'] ).all()
    for msg in messages:
        time = json.dumps(msg.time_stamp, default = myconverter)
        time = time.strip('"')
        send({'msg': msg.message, 'username':msg.username, 'time_stamp': time,'room':data['room']})
    send({'msg': data['username'] + " has joined the room."}, room=data['room'])
    emit('scrollToBottom')

@socketio.on('leave')
def leave(data):
    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + data['display_name'] + " room."}, room=data['room'])
    
    
@socketio.on('cardDragStart')
def cardDragStart(data):
    emit('cardDragging', data, broadcast=True)

@socketio.on('cardDrop')
def cardDrop(json):
    card_id = json["id"]
    card_id = card_id[5:len(card_id)] #cutting off the "card_"
    stmt = db.session.query(Card).get(card_id)
    stmt.sprint_id = json["newSprint"]
    stmt.status = json['status']
    if stmt.status == 'backlog':
        stmt.sprint_id = 0
    db.session.commit()
    emit('cardDrop', json, broadcast=True)

@socketio.on('addSprint')
def addSprint(json):
    toAdd = Sprint(project_id=json["id"], sprint_num = json["sprint"])
    db.session.add(toAdd)
    db.session.commit()
    print(json["sprint"])
    emit('sprintCreate', {'sprint_id' : json["sprint"], 'project_id' : json["id"]}, broadcast = True) 
    
@socketio.on('cardClick')
def cardClick(json):
    card_id = json["id"]
    stmt = db.session.query(Card).get(card_id)
    if json['displayed'] == stmt.title:
        json = stmt.description
        ele_id = "card_"+ str(card_id)
        emit('cardClick', {'json':json, 'id':ele_id })
    else:
        json = stmt.title
        ele_id = "card_"+ str(card_id)
        emit('cardClick', {'json':json, 'id':ele_id })

@socketio.on('cardEdit')
def cardEdit(json):
    card = db.session.query(Card).filter_by(id=json['card_id']).first_or_404()
    old_title = card.title
    old_description = card.description
    new_title = json['new_title']
    new_description = json['new_description']
    print(old_title)
    print(new_title)
    print(old_description)
    print(new_description)
    print(not new_title)
    if new_title:
        if new_description:
            if old_title != new_title or old_description != new_description:
                card.title = new_title
                card.description = new_description
                db.session.commit()
                print('here')
                emit('cardEdit',{'card_id':card.id,'new_title':new_title,'new_description':new_description,'old_title':old_title,'old_description':old_description}, broadcast = True)

@socketio.on('cardDelete')
def cardDelete(json):
    toDelete = db.session.query(Card).filter_by(id=json['card_id']).first_or_404()
    db.session.delete(toDelete)
    db.session.commit()
    emit('cardDelete', {'card_id' : json['card_id']}, broadcast = True)


@socketio.on('cardPriority')
def cardPriority(json):
    card = db.session.query(Card).filter_by(id=json['card_id']).first_or_404()
    if card.priority == 'black':
        card.priority = 'red'
    elif card.priority == 'red':
        card.priority = 'blue'
    else:
        card.priority = 'black'
    db.session.commit()
    emit('cardPriority', {'card_id' : json['card_id'], 'priority':card.priority}, broadcast = True)

@socketio.on('cardInfo')
def cardInfo(json):
    card = db.session.query(Card).filter_by(id=json['card_id']).first_or_404()
    info = [card.title,card.description]
    emit('cardInfo',{'title':card.title,'description':card.description,'card_id':json['card_id']})
 
@socketio.on('cardAssigned')
def cardAssignments(json):
    card = db.session.query(Card).filter_by(id=json['card_id']).first_or_404()
    info = card.assigned
    print(info)
    emit('cardAssigned',{'assigned':info,'card_id':json['card_id']})

@socketio.on('sprintDelete')
def sprintDelete(json):
    sprints = db.session.query(Sprint).filter_by(project_id=json['project_id']).all()
    for spr in sprints:
        if spr.sprint_num == int(json['sprintNum']):
            cards_in_sprint = db.session.query(Card).filter_by(sprint_id=json['sprintNum'],project_id=json['project_id']).all()
            for card in cards_in_sprint:
                card.status = 'backlog'
                card.sprint_id = 0
                db.session.commit()
                card_id = 'card_'+str(card.id)
                emit('cardReset', {'id':card_id}, broadcast=True)
            db.session.delete(spr)
            db.session.commit()
            sprintID = 'Sprint '+str(json['sprintNum'])
            emit('deleteSprint',{'id':sprintID,'project_id':json['project_id']},broadcast = True)
        if spr.sprint_num > int(json['sprintNum']):
            cards_in_sprint = db.session.query(Card).filter_by(sprint_id=spr.sprint_num,project_id=json['project_id']).all()
            for card in cards_in_sprint:
                card.sprint_id = card.sprint_id -1
                db.session.commit()
            sprintID = 'Sprint '+str(spr.sprint_num)
            newsprintID = 'Sprint '+str(spr.sprint_num - 1)
            spr.sprint_num = spr.sprint_num -1
            db.session.commit()
            emit('sprintDecrement',{'project_id':json['project_id'],'id':sprintID,'new_id':newsprintID},broadcast = True)

@socketio.on('getMembers')
def getMembers(json):
    user = User.query.filter_by(username = json['username']).first_or_404()
    subss  = db.session.query(subs).all()
    for sub in subss:
        user = User.query.filter_by(id = sub[0]).first_or_404()
        if (sub[1] == json['project_id'] and user.username != json['username']):
            emit('buildUserList',{'project_id':json['project_id'],'user_id':user.id,'username': user.username,'image_file':user.image_file})

@socketio.on('getAllMembers')
def getAllMembers(json):
    user = User.query.filter_by(username = json['username']).first_or_404()
    subss  = db.session.query(subs).all()
    for sub in subss:
        user = User.query.filter_by(id = sub[0]).first_or_404()
        if (sub[1] == json['project_id']):
            emit('buildUserListAll',{'project_id':json['project_id'],'user_id':user.id,'username': user.username,'image_file':user.image_file})
    emit('getAllMembersDone',{'project_id':json['project_id']})    

@socketio.on('createDirectMessagingRoom')
def createDirectMessagingRoom(json):
    project_id = json['project_id']
    user = User.query.filter_by(username = json['username']).first_or_404()
    other_user = User.query.filter_by(id = json['otheruser_id']).first_or_404()
    if(user.id < other_user.id):
        room_title = str(user.id)+":"+user.username+":"+str(other_user.id)+":"+other_user.username
        users = str(user.id)+":"+str(other_user.id)
        username_list = user.username +":"+ other_user.username
        new_room = Channel(project_id=project_id,room=room_title,users = users)
        duplicate = db.session.query(Channel).filter_by(room = room_title,users = users).first()
        if duplicate == None:
            db.session.add(new_room)
            db.session.commit()
    
    else:
        room_title = str(other_user.id)+":"+other_user.username+":"+str(user.id)+":"+user.username
        users = str(other_user.id)+":"+str(user.id)
        username_list = user.username +":"+ other_user.username
        new_room = Channel(project_id=project_id,room=room_title,users = users)
        duplicate = db.session.query(Channel).filter_by(room = room_title,users = users).first()
        if duplicate == None:
            db.session.add(new_room)
            db.session.commit()
    
    
    emit('displayNewDMRoom',{'project_id':project_id, 'username_list':username_list,'room_id':room_title},broadcast=True)


@socketio.on('createGroupMessagingRoom')
def createGroupMessagingRoom(json):
    project_id = json['project_id']
    room_title = json['roomName']
    user = User.query.filter_by(username = json['username']).first_or_404()
    username_list = ""
    user_list = ""
    tosort = [user.id]
    for x in json['users']:
        tosort.append(int(x))
    print(tosort)
    mylist = sorted(tosort)
    print(mylist)
    for user in mylist:
        user_list += ":"+str(user)
        user = User.query.filter_by(id = user).first_or_404()
        username_list += ":"+user.username
        print(username_list)
    duplicate = db.session.query(Channel).filter_by(room = room_title,users = user_list).first()
    if duplicate == None:
        new_room = Channel(project_id=project_id,room=room_title,users = user_list)
        db.session.add(new_room)
        db.session.commit()
        emit('displayNewGroupRoom',{'project_id':project_id,'room_title':room_title,'username_list':username_list},broadcast=True)
    
@socketio.on('assignChecks')
def assignChecks(json):
    card = db.session.query(Card).filter_by(id=json['card_id']).first_or_404()
    project_id = card.project_id
    new_string = ""
    old_list = card.assigned
    old_list = old_list.split(":")
    old_list = sorted(old_list)
    new_list = []
    assignment_list = json['checkedUsers']
    for x in assignment_list:
        int(x)
        user = db.session.query(User).filter_by(id= x).first_or_404()
        new_list.append(user.username)
        new_string += user.username +":"
    
    card_assigned = False
    if (len(new_list) == 0):
        emit('setAssignmentUnassigned',{'card_id':json['card_id']},broadcast=True)
    
    if  (len(old_list) == 1 and len(new_list) > 0):
        emit('setAssignmentOff',{'card_id':json['card_id']},broadcast=True)
    
    if (len(new_list)>0):
        card_assigned = True    
    for x in new_list:
        if x not in old_list:
            emit('setAssignmentOn',{'username':x,'card_id':json['card_id']}, broadcast= True)
    for y in old_list:
        if y not in new_list and y != "" and card_assigned:
            emit('setUserAssignmentOff',{'username':y,'card_id':json['card_id']}, broadcast = True)
    card.assigned = new_string
    db.session.commit() 

@socketio.on('allAssignments')
def allAssignments(json):
    cards = db.session.query(Card).filter_by(project_id = json['project_id']).all()
    for card in cards:
        users_assigned = card.assigned
        users_assigned = users_assigned.split(":")
        if (len(users_assigned) == 1):
            emit('setAssignmentUnassigned',{'card_id':card.id})
        for user in users_assigned:
            emit('setAssignmentOn',{'username':user,'card_id':card.id})

@socketio.on('getChannels')
def getChannels(json):
    channels = db.session.query(Channel).filter_by(project_id = json['project_id']).all()
    user = db.session.query(User).filter_by(username = json['username']).first_or_404()
    my_id = str(user.id)
    print(user.username)
    for channel in channels:
        print(channel.id)
        ids = channel.users.split(":")
        print(ids)
        if(len(ids) > 2):
            print(str(user.id))
            if(my_id in ids):
                username_list = ""
                for id in ids:
                    if id != "":
                        user = db.session.query(User).filter_by(id = id).first_or_404()
                        username_list += user.username+":"
                print(username_list)
                emit('displayNewGroupRoom',{'project_id':channel.project_id,'room_title':channel.room,'username_list':username_list})
        else:
            if(my_id in ids):
                username_list = ""
                for id in ids:
                    user = db.session.query(User).filter_by(id = id).first_or_404()
                    username_list += user.username+":"
                emit('displayNewDMRoom',{'project_id':channel.project_id, 'username_list':username_list,'room_id':channel.room})
        
        
@socketio.on('deleteChannel')
def deleteChannel(json):
    print(json['channelName'])
    channelName = json['channelName']
    channel = db.session.query(Channel).filter_by(room = channelName, project_id = json['project_id']).first()
    if channel != None:
        channel_users = channel.users.split(":")
        msgs = db.session.query(Chat_History).filter_by(room =channel.room, project_id = json['project_id']).all()
        for msg in msgs:
            db.session.delete(msg)
        db.session.delete(channel)
        db.session.commit()
        emit('removeGroupChannelFromList',{'project_id':json['project_id'], 'channelName':channel.room}, broadcast = True)  
    else:
        room_title= ""
        user = db.session.query(User).filter_by(username = json['username']).first()
        other_user = db.session.query(User).filter_by(username =json['channelName']).first()
        if(user.id < other_user.id):
            room_title = str(user.id)+":"+user.username+":"+str(other_user.id)+":"+other_user.username
        else:
            room_title = str(other_user.id)+":"+other_user.username+":"+str(user.id)+":"+user.username
        print(room_title)
        channel = db.session.query(Channel).filter_by(room = room_title, project_id = json['project_id']).first()
        msgs = db.session.query(Chat_History).filter_by(room =channel.room, project_id = json['project_id']).all()
        for msg in msgs:
            db.session.delete(msg)
        db.session.delete(channel)
        db.session.commit()
        emit('removeDMChannelFromList',{'username':user.username, 'other_username':other_user.username,'project_id':json['project_id']},broadcast=True)
        