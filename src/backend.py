from flask import Flask, make_response, jsonify, render_template
from storage import StorageSQLite, StorageJSON
import sqlite3


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


def retrieve_data(cursor, index):
    query = '''
    SELECT
        date,
        volume_of_trade,
        price_at_opening,
        min_price,
        max_price,
        price_at_closure
    FROM {0};
    '''.format(index)
    cursor.execute(query)
    response = cursor.fetchall()

    headers = [
        'index',
        'date',
        'volume_of_trade',
        'price_at_opening',
        'min_price',
        'max_price',
        'price_at_closure'
    ]

    records = []
    for row in response:
        upd_row = tuple([index] + list(row))
        record = dict(zip(headers, upd_row))
        records.append(record)

    return records


@app.route("/data", methods=["GET"])
def home():
    try:
        conn = sqlite3.connect(DATABASE + '.db')
        cursor = conn.cursor()
        records = []
        for index in ['IMOEX', 'TMOS', 'EQMX', 'SBMX']:
            records.extend(retrieve_data(cursor, index))

        return jsonify({'records': records}), 200
    except Exception:
        return jsonify({'error': 'Couldn\'t get a record from the database'}), 500


@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')


@app.route("/kde-plot", methods=["GET"])
def kde_plot():
    return render_template('kde-plot.html')


@app.route("/heatmap", methods=["GET"])
def heatmap():
    return render_template('heatmap.html')


@app.route("/bubbles", methods=["GET"])
def bubbles():
    return render_template('bubbles.html')


@app.route("/bar-plot", methods=["GET"])
def bar_plot():
    return render_template('bar-plot.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8079, debug=True)
