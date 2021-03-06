from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO, send


app = Flask(__name__)
app.config['SECRET_KEY'] = '508d2c80b4056ad1e9d9969224d3fcbd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db?charset=utf8mb4'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from app import routes