import sqlite3
import json

conn = sqlite3.connect('moex.db')
cursor = conn.cursor()
query = '''
    SELECT
        date,
        volume_of_trade,
        price_at_opening,
        min_price,
        max_price,
        price_at_closure
    FROM {0};
    '''.format('MCFTRR')
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
    upd_row = tuple(['MCFTRR'] + list(row))
    record = dict(zip(headers, upd_row))
    records.append(record)
with open('../data/MCFTRR.json', 'w', encoding='UTF-8') as f:
    f.write(json.dumps(records, indent=4))
# opening = 'opening'
# ticker = 'TMOS'
# date = '24/02/2022'
# query = '''select {0}
#                from moex
#                where ticker='{1}' and date='{2}'
#             '''.format(opening, ticker, date)
# cursor.execute(query)
# response = cursor.fetchall()
# print(response[0])
conn.close()
