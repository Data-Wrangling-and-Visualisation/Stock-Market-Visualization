import sqlite3

conn = sqlite3.connect('moex.db')
cursor = conn.cursor()
cursor.execute('drop table moex')
cursor.execute('''
               create table if not exists moex(
               ticker varchar(10),
               date varchar(10),
               opening int,
               closing int,
               primary key(ticker, date)
               )
               ''')
conn.commit()

cursor.execute('''insert into moex values('TMOS', '24/02/2022', 10, 5)''')
cursor.execute('''insert into moex values('TMOS', '23/02/2022', 9, 10)''')
conn.commit()
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
