from flask import Flask, request, make_response, jsonify
from storage import StorageSQLite, StorageJSON
import sqlite3
import datetime


DATABASE = 'moex'
db_storage = StorageSQLite()

# JSON storage
json_storage = StorageJSON()

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def server_error(error):
    return make_response(jsonify({'error': 'Internal server error, probably related to the database'}), 500)


@app.route("data/price/<string:index>?<string:date>?<string:opening>", methods=["GET"])
def load_price_data(index: str, ticker: str):
    global json_storage
    try:
        index = request.args.get('index')
        date = request.args.get('date')
        datetime.date.fromisoformat(date)
        opening = opening = 'price_at_opening' if request.args.get('opening') == 'true' else 'price_at_closing'

        conn = json_storage.connect('/data')
        df = json_storage.read(conn, index)

        return jsonify({'price': df[df['date'] == date][opening]}), 201
    except KeyError as e:
        return jsonify({'error': f'Key was not found: {e.__str__()}'}), 404
    except FileNotFoundError as e:
        return jsonify({'error': f'File was not found: {e.__str__()}'}), 404
    except ValueError:
        return jsonify({'error': "'Incorrect data format, should be YYYY-MM-DD'"}), 404


@app.route("/db/price/<string:ticker>", methods=["GET"])
def home(ticker):
    try:
        date = request.args.get('date')
        opening = 'price_at_opening' if request.args.get('opening') == 'true' else 'price_at_closing'
    except KeyError:
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
    except Exception:
        return jsonify({'error': 'Couldn\'t get a record from the database'}), 500


if __name__ == "__main__":
    app.run(debug=True)
