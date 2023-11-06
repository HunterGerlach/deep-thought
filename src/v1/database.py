import sqlite3

dbase = sqlite3.connect('deep_thought.db') # Open a database File
print('Database opened')


dbase.execute(''' CREATE TABLE IF NOT EXISTS chat_history(
    ID INT PRIMARY KEY NOT NULL,
    MESSAGE TEXT NOT NULL,
    TYPE TEXT NOT NULL,
    TIMESTAMP TEXT NOT NULL,
    GCHATID TEXT NOT NULL,
    SLACKID INT NOT NULL) ''')

print('Table created')

def insert_record(ID,MESSAGE,TYPE,TIMESTAMP,GCHATID,SLACKID):
    dbase.execute(''' INSERT OR IGNORE INTO chat_history(ID,MESSAGE,TYPE,TIMESTAMP,GCHATID,SLACKID)
        VALUES(?,?,?,?,?,?)
''',(ID,MESSAGE,TYPE,TIMESTAMP,GCHATID,SLACKID))
    dbase.commit()
    print('REcord inserted')


def read_Data():
    # from math import *
    data = dbase.execute(''' SELECT * FROM chat_history''')
    for record in data:
        print('ID : '+str(record[0]))
        print('MESSAGE : '+str(record[1]))
        print('TYPE : '+str(record[2]))
        print('TIMESTAMP : '+str(record[3])+'\n')
        print('GCHATID : '+str(record[2]))
        print('SLACKID : '+str(record[3])+'\n')
