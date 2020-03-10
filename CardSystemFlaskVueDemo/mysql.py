from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
import yaml

app = Flask(__name__)
db = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)

mysql = MySQL(app)
CORS(app)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '!Row10913696'
app.config['MYSQL_DB'] = 'carddb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

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


if __name__ == '__main__':
    app.run(debug=True)
