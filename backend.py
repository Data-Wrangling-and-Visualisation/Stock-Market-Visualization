from flask import Flask, request, make_response, jsonify, g
from storage import StorageSQLite
import sqlite3


DATABASE = 'moex'
storage = StorageSQLite()
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
        opening = 'price_at_opening' if request.args.get('opening') == 'True' else 'price_at_closing'
    except:
        return {'error': 'Specify date in format yyyy-mm-dd'}, 404

    # Currenly won't work if the specified date is a holiday (i.e. exchange didn't work)
    try:
        conn = sqlite3.connect(DATABASE + '.db')
        cursor = conn.cursor()
        query = '''
                select {0}
                from {1}
                where date='{2}'
                '''.format(opening, ticker, date)
        cursor.execute(query)
        response = cursor.fetchone()
        conn.close()
        return jsonify({'price': float(response[0])}), 200
    except:
        return jsonify({'error': 'Couldn\'t get a record from the database'}), 500
    
if __name__ == "__main__":
    app.run(debug=True)