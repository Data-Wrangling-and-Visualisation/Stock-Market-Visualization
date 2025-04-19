import sqlite3

conn = sqlite3.connect('moex.db')
cursor = conn.cursor()
cursor.execute('''
                select price_at_opening from TMOS
                where date='2024-11-01';
               ''')
response = cursor.fetchall()
print(response)
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
