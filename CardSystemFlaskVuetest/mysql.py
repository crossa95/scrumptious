from flask import Flask, jsonify, request, render_template, abort, redirect, url_for, make_response, session
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
import yaml

app = Flask(__name__)
db = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)
socketio = SocketIO(app, cors_allowed_origins="*")

mysql = MySQL(app)
CORS(app)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '!Row10913696'
app.config['MYSQL_DB'] = 'carddb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

app.debug = True

@app.route('/api/cards', methods=['GET'])
def get_all_cards():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM carddb.cardsyst")
    rv = cur.fetchall()
    return jsonify(rv)


@app.route('/api/card', methods=['POST'])
def add_card():
    cur = mysql.connection.cursor()
    card_description = request.get_json()['card_description']

    cur.execute("INSERT INTO carddb.cardsyst (card_description) VALUES ('" + str(card_description) +
                "')")
    mysql.connection.commit()

    result = {'card_description': card_description}

    return jsonify({'result': result})


@app.route('/api/card/<card_id>', methods=['PUT'])
def update_card(card_id):
    cur = mysql.connection.cursor()
    card_description = request.get_json()['card_description']

    cur.execute("UPDATE carddb.cardsyst SET card_description = '" + str(card_description) +
                "' where card_id = " + card_id)
    mysql.connection.commit()

    result = {'card_description': card_description}

    return jsonify({'result': result})


@app.route('/api/card/<card_id>', methods=['DELETE'])
def delete_card(card_id):
    cur = mysql.connection.cursor()
    response = cur.execute("DELETE FROM carddb.cardsyst where card_id = " + card_id)
    mysql.connection.commit()

    if response > 0:
        result = {'message': 'record deleted'}
    else:
        result = {'message': 'no record found'}

    return jsonify({'result': result})

@app.route('/login1', methods = ['GET','POST'])
def login1():
    if request.method == 'POST':
        user = request.get_json()["user"]
        passwd = request.get_json()["pass"]
        emails  = getemaillist()
        emails = emails.replace("[","")
        emails = emails.replace("]","")
        emails = emails.replace('"',"")
        emaillist = emails.split(",")
        
        
        x = len(emaillist)-1 
        while x >= 0:
            print(emaillist[x])
            print(user)
            if (user == emaillist[x]):    
                p = getpass(emaillist[x])
                if(p == passwd):
                   app.logger.debug("Login request from " + user)
                   session["user"] = user
                   print(session)
                   return redirect(url_for('chat'))
                else:
                    app.logger.debug("Login request from "+ user)
                    return redirect(url_for('error1'))
            else:
                x= x-1
                if(x == -1):
                    app.logger.debug("Login request form "+ user)
                    return redirect(url_for('error1'))
        
    else:
        return render_template("login.html")

@app.route('/chat', methods = ['GET','POST'])
def chat():
    if 'user' not in session:
        return redirect(url_for('error1'))
    else:
        return  render_template('session.html')

@app.route('/error1')
def error1():
    return render_template("error.html")
        
def messageReceived(methods=['GET', 'POST']):
     print('message was received!!!')

# Get all users' full names
def getnames():
        answer = []
        cur = conn.cursor()
        cur.execute("select user.f_name,user.l_name "
        "from user;") 
        for f_name, l_name in cur.fetchall():
             answer.append(f_name + " " + l_name)
        return json.dumps(answer)

def getemaillist():
    answer = []
    cur = conn.cursor()
    cur.execute("select user.email " "from user;")
    for email in cur.fetchall():
        answer.append(email)
    return json.dumps(answer)

def getpass(emailaddress):
    answer = []
    cur = conn.cursor()
    cur.execute("select user.password " "from user " "where user.email = '%s'" %emailaddress)
    for password in cur.fetchall():
        answer.append(password)
    return json.dumps(answer)

def getdisplayname(emailaddress):
    answer = []
    cur = conn.cursor()
    cur.execute("select user.display_name " "from user " "where user.email = '%s'" %emailaddress)
    for display_name in cur.fetchall():
        answer.append(display_name)
    return json.dumps(answer)

#user data. Login required
@app.route("/userinfo", methods = ['GET'])
def userinfo():
    print(session)
    if 'user' not in session:
        return redirect(url_for('error'))
    else:
        answer = getdisplayname("ab@ab.com")
        return answer

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
        print('received my event: ' + str(json))
        socketio.emit('my response', json, callback=messageReceived)

if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app, host='0.0.0.0', port=5000)
