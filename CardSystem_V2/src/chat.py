from flask import Flask, render_template, request, abort, redirect, url_for, make_response, session
from flask_socketio import SocketIO, send, emit
import MySQLdb
import configparser
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = b'\xc5\x1dh\x8a\xd3\xc7\x92\xf5$\xf6ql\xef\xb73\x99'

socketio = SocketIO(app, cors_allowed_origins="*")

app.debug = True

config = configparser.ConfigParser()
config.read('./config.ini')
hostname = config.get('config', 'hostname')
username = config.get('config', 'username')
database = config.get('config', 'database')
password = config.get('config', 'password')

conn = MySQLdb.connect(
        host = hostname,
        user = username,
        passwd = password,
        db = database)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.get_json()["user"]
        if (user == "John") or (user == "Jim"):    
            app.logger.debug("Login request from " + user)
            session["user"] = user
            return redirect(url_for('chat'))
        else:
            app.logger.error("Invalid login from "+user)
            return redirect(url_for('error')), 404
    else:
        return render_template("login.html")

@app.route('/chat')
def chat():
    if 'user' not in session:
        return redirect(url_for('error'))
    else:
        return  render_template('session.html')

@app.route('/error')
def error():
    return render_template("error.html")
        

def messageReceived(methods=['GET', 'POST']):
     print('message was received!!!')

# Get all users' full names
def getnames():
        answer = []
        cur = conn.cursor()
        cur.execute("select user.f_name,user.l_name"
        "from user"
        )                                               
        
        for f_name, l_name in cur.fetchall():
             answer.append(f_name + " " + l_name)
        return json.dumps(answer)

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
        print('received my event: ' + str(json))
        socketio.emit('my response', json, callback=messageReceived)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
