import sqlite3

db = sqlite3.connect('Top-10-movies.db')
cursor = db.cursor()
#cursor.execute('DROP TABLE top10movies')

cursor.execute('CREATE TABLE top10movies(id INTEGER PRIMARY KEY, title varchar(250) NOT NULL UNIQUE, year INTEGER NOT NULL , description varchar(250) NOT NULL, rating FLOAT NOT NULL , ranking INTEGER , review varchar(250) NOT NULL, img_url varchar(250) NOT NULL)')

db.commit()