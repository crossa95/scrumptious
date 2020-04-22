from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

# Everytime you make a model, remember that you have to import it into other .py files like routes.py for example

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# this is how to make a connection between models if you want to have a many-to-many relationship
# in this case I want to this relationship between users and projects because a user
# can make many projects and a proejct can have many users be a part of it

subs = db.Table('subs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
)

class User(db.Model, UserMixin):
    # every row needs a primary key which auto increments
    # when you make a user or whatevery table, you don't need to specify the id associated with it
    # it does it automatically
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    # The reason I don't have to specify this in Project as well is because at the very end of this statement, you can see that I already
    # specify Project's relationship with user
    projects_part_of = db.relationship('Project', secondary=subs, backref=db.backref('users_in', lazy = 'dynamic'))

    # this bit is how it shows up when I query it
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    description = db.Column(db.Text, nullable=False)
    cards = db.relationship('Card', backref='author', lazy=True)

    def __repr__(self):
        return f"Project('{self.title}', '{self.date_posted}')"

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default = 'backlog')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    sprint_id = db.Column(db.Integer, default = 0)

    def __repr__(self):
        return f"Card('{self.title}', '{self.description}')"


class Chat_History(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    message = db.Column('message',db.String(500))
    username = db.Column('username', db.String(20), nullable=False)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    room = db.Column('room',db.String(20),nullable = False)
    project_id = db.Column(db.Integer, nullable=False, default=1)
    def __repr__(self):
        return f"Msg('{self.message}')"



class Sprint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    sprint_num = db.Column(db.Integer, nullable=False, default =1)

    def __repr__(self):
        return f"Msg('{self.sprint_num}')"
    
db.create_all()
