from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
import requests
import sqlite3


app = Flask(__name__)
Bootstrap5(app)

# CREATE DB
db = sqlite3.connect('Top-10-movies.db', check_same_thread=False)
db.row_factory = sqlite3.Row
cursor = db.cursor()

API_SEARCH_DB_URL = 'https://api.themoviedb.org/3/search/movie'
API_MOVIE_DETAILS = 'https://api.themoviedb.org/3/movie'
IMAGES_URL_PREFIX = 'https://image.tmdb.org/t/p/original'

API_KEY = 'c63b4c0c7df4700b5da8016dabc5b0a9'

# CREATE TABLE
# cursor.execute('CREATE TABLE top10movies(id INTEGER PRIMARY KEY, title varchar(250) NOT NULL UNIQUE, year INTEGER NOT NULL , description varchar(250) NOT NULL, rating FLOAT NOT NULL , ranking INTEGER NOT NULL UNIQUE , review varchar(250) NOT NULL, img_url varchar(250) NOT NULL)')
# db.close()
# cursor.execute('INSERT INTO top10movies(title, year, description, rating, ranking, review, img_url) VALUES(?,?,?,?,?,?,?)', ("Phone Booth",2002,"Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",7.3,10,"My favourite character was the caller.","https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"))
# cursor.execute('INSERT INTO top10movies(title, year, description, rating, ranking, review, img_url) VALUES(?,?,?,?,?,?,?)', (
#     "Avatar The Way of Water",
#     2022,
#     "Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     7.3,
#     9,
#     "I liked the water.",
#     "https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# ))
#db.commit()

@app.route("/")
def home():
    cursor.execute('SELECT * FROM top10movies ORDER BY rating DESC')
    movies = cursor.fetchall()
    ranking = 0
    for movie in movies:
        ranking = ranking + 1
        cursor.execute('UPDATE top10movies SET ranking = ? WHERE id =?',(ranking,movie['id']))
    db.commit()

    cursor.execute('SELECT * FROM top10movies ORDER BY rating')
    the_movies = cursor.fetchall()
    return render_template("index.html" , all_movies = the_movies)

@app.route("/edit", methods=['GET','POST'])
def edit_rating():
    if request.method == 'POST':
        updated_rating = request.form['rating']
        updated_review = request.form['review']
        updated_movies_id = request.form['id']
        cursor.execute('UPDATE top10movies SET rating=? , review=? WHERE id =?',(updated_rating,updated_review,updated_movies_id))
        db.commit()
        return redirect(url_for('home'))
    movie_id = request.args.get('id')
    cursor.execute('SELECT * FROM top10movies WHERE id = ?',(movie_id,))
    the_movie = cursor.fetchone()
    return render_template('edit.html', the_movie = the_movie)

@app.route('/delete')
def delete_movie():
    movie_id = request.args.get('id')
    cursor.execute('DELETE FROM top10movies WHERE id = ?',(movie_id,))
    db.commit()
    return redirect(url_for('home'))

@app.route('/addmovie', methods = ['GET','POST'])
def add_movie():
    if request.method == 'POST':
        new_movie_title = request.form['addmovie']
        print(new_movie_title)
        response = requests.get(API_SEARCH_DB_URL, params={'api_key': API_KEY , 'query': new_movie_title},timeout=10)
        data = response.json()
        result = data['results']
        return render_template('select.html', options = result)
    return render_template('add.html')

@app.route('/adding')
def adding_movie():
    id = request.args.get('id')
    SELECTED_MOVIE_URL = f'{API_MOVIE_DETAILS}/{id}'
    response = requests.get(SELECTED_MOVIE_URL, params={'api_key': API_KEY})
    data = response.json()
    newmovie_title = data['original_title']
    newmovie_description = data["overview"]
    newmovie_year = data["release_date"][:4]
    poster_path = data["poster_path"]
    newmovie_img_url = f'{IMAGES_URL_PREFIX}{poster_path}'
    cursor.execute('INSERT INTO top10movies(title, year, description, rating, ranking, review, img_url) VALUES(?,?,?,?,?,?,?)',(newmovie_title,newmovie_year,newmovie_description,0,None,'',newmovie_img_url))
    db.commit()
    cursor.execute('SELECT * FROM top10movies WHERE title = ?',(newmovie_title,))
    added_movie= cursor.fetchone()
    return render_template('edit.html', the_movie =added_movie)


if __name__ == '__main__':
    app.run(debug=True)
