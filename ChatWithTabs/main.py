from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
# All of the SQL utilities and configs are commented out for now
#from flask_mysqldb import MySQL

# define app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'blahblahblah#'
socketio = SocketIO(app, cors_allowed_origins="*")

#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'seniorproject'
#app.config['MYSQL_PASSWORD'] = 'password'
#app.config['MYSQL_DB'] = 'seniorproject'

#define app route. for demo only one page needed
@app.route('/')
def sessions():
    return render_template('session.html')


#outputs browser console
def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

#write event without room specification
@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

#write event with room specification 
#works with the script.js file
#currently needs to be altered
#can mock user[] (userlist)
@socketio.on('private_message', namespace = '/private')
def private_message(payload):
    recipient_session_id = users[payload['username']]
    message = payload['message']
    emit('new_private_message', message, room=recipient_session_id)



if __name__ == '__main__':
    socketio.run(app, debug=True)
