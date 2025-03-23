from flask import Flask, request, make_response, jsonify, g
import sqlite3
import os

DATABASE = 'moex'

app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def server_error(error):
    return make_response(jsonify({'error': 'Internal server error, probably related to the database'}), 500)
  

@app.route("/price/<string:ticker>", methods=["GET"])
def home(ticker):
    try:
        date = request.args.get('date')
        opening = 'opening' if request.args.get('opening') == 'True' else 'closing'
    except:
        return 404

    try:
        conn = sqlite3.connect(DATABASE + '.db')
        cursor = conn.cursor()
        query = '''select {0}
                from {1}
                where ticker='{2}' and date='{3}'
                '''.format(opening, DATABASE, ticker, date)
        cursor.execute(query)
        response = cursor.fetchone()
        conn.close()
        return jsonify({'price': response[0]}), 200
    except:
        return 500
    
if __name__ == "__main__":
    app.run(debug=True)