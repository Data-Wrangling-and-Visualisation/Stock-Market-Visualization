import sqlite3
import json

# Индексы хуйня, остальное норм

conn = sqlite3.connect('moex.db')
cursor = conn.cursor()
query = '''
    SELECT COUNT(*)
    FROM {0};
    '''.format('IMOEX')
cursor.execute(query)
cursor.connection.commit()
response = cursor.fetchall()
print(response)

# headers = [
#     'index',
#     'date',
#     'volume_of_trade',
#     'price_at_opening',
#     'min_price',
#     'max_price',
#     'price_at_closure'
# ]

# records = []
# for row in response:
#     print(row)
# with open('../data/MCFTRR.json', 'w', encoding='UTF-8') as f:
#     f.write(json.dumps(records, indent=4))

conn.close()
