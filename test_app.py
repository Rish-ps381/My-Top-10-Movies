import pytest
import sqlite3
from main import app

@pytest.fixture
def client():
    # Setup Flask test client
    app.config['TESTING'] = True

    # Create in-memory SQLite database
    connection = sqlite3.connect(':memory:', check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Create table schema
    cursor.execute('''
        CREATE TABLE top10movies(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            description TEXT NOT NULL,
            rating FLOAT NOT NULL,
            ranking INTEGER,
            review TEXT NOT NULL,
            img_url TEXT NOT NULL
        )
    ''')

    # Insert one movie record
    cursor.execute('''
        INSERT INTO top10movies (title, year, description, rating, ranking, review, img_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ("Inception", 2010, "Dream within a dream", 9.0, 1, "Excellent", "https://image.url"))
    connection.commit()

    # Patch global db + cursor in app
    app.db = connection
    app.cursor = cursor

    with app.test_client() as client:
        yield client

    connection.close()


def test_home_route(client):
    """Test if home route loads and shows movie"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Inception" in response.data


def test_edit_get_route(client):
    """Test GET /edit route"""
    response = client.get('/edit?id=1')
    assert response.status_code == 200
    assert b"Inception" in response.data


def test_edit_post_route(client):
    """Test POST /edit updates rating and review"""
    response = client.post('/edit', data={
        'id': 1,
        'rating': 8.5,
        'review': 'Mind-blowing!'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Verify update in DB
    app.cursor.execute('SELECT * FROM top10movies WHERE id=1')
    movie = app.cursor.fetchone()
    assert movie['rating'] == 8.5
    assert movie['review'] == 'Mind-blowing!'


def test_delete_movie(client):
    """Test deleting a movie"""
    response = client.get('/delete?id=1', follow_redirects=True)
    assert response.status_code == 200

    # Verify deletion
    app.cursor.execute('SELECT * FROM top10movies WHERE id=1')
    deleted = app.cursor.fetchone()
    assert deleted is None


def test_add_movie_get(client):
    """Test add movie form page loads"""
    response = client.get('/addmovie')
    assert response.status_code == 200
