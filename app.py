import logging
import os

from flask import Flask, flash, redirect, url_for, request, render_template
from data_manager import DataManager
from models import db

data_manager = DataManager()
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_errors.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(module)s.%(funcName)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE_PATH, mode='a')
    ]
)


app = Flask(__name__)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SECRET_KEY'] = 'movies-rule'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route('/', methods=['GET'])
def home():
    """
    Renders the home page (index.html), displaying a list of all users.

    Returns:
        str: Rendered HTML template.
    """
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def users():
    """
    Handles the creation of a new user via a POST request (JSON payload).

    Returns:
        tuple: JSON response with status ('success' or 'error') and HTTP status code.
    """
    try:
        data = request.get_json()
        name = data.get('name')
        if name is None:
            return "Please enter name.", 400

        new_user = data_manager.create_user(name)
        if new_user is not None:
            flash(f"✔️ User {name} has been added!", 'success')
            return {'status': 'success'}, 200
        else:
            flash(f" ❌ Error in creating user {name}. Please Try again.", 'error')
            return {'status': 'error'}, 200
    except Exception as e:
        return f"JSON Error: {e}", 400


@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def movies(user_id):
    """
    GET: Renders the movies page for a specific user, displaying their favorite movies.
    POST: Adds a new movie to the user's favorites (via JSON payload and OMDb API lookup).

    Args:
        user_id (int): The ID of the user whose movies are being accessed.

    Returns:
        str/tuple: Rendered HTML template (GET) or JSON response (POST).
    """
    if request.method == 'POST':
        try:
            data = request.get_json()
            title = data.get('title')
            if title is None:
                return "Please enter movie title", 400
            user = data_manager.get_user_by_id(user_id)
            user_name = user.user_name if user else f"User {user_id}"
            new_movie = data_manager.add_movie(user_id, title)
            redirect_url = url_for('movies', user_id=user_id)
            if new_movie is not None:
                flash(f"✔️ Movie '{new_movie.title}' has been added for {user_name}!", 'success')
                return {'status': 'success'}, 200
            else:
                flash(f" ❌ Error in creating movie '{title}'. Please Try again.", 'error')
                return {'status': 'error'}, 200
        except Exception as e:
            return f"JSON Error: {e}", 400

    else:
        user = data_manager.get_user_by_id(user_id)
        user_name = user.user_name if user else f"User {user_id} (Not Found)"
        fav_movies = data_manager.get_movies(user_id)
        return render_template('movies.html',
                               user_id=user_id,
                               user_name=user_name,
                               movies=fav_movies)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update(user_id, movie_id):
    """
    Updates the title of a specific movie (via JSON payload).

    Args:
        user_id (int): The ID of the user (used for URL consistency, but not logic).
        movie_id (int): The ID of the movie to be updated.

    Returns:
        tuple: JSON response with status ('success' or 'error') and HTTP status code.
    """
    try:
        data = request.get_json()
        new_title = data.get('new_title')
        if new_title is None:
            return "Please enter new movie title", 400

        updated_movie = data_manager.update_movie(movie_id, new_title)
        if updated_movie:
            flash(f"✔️ Movie '{new_title}' has been updated!", 'success')
            return {'status': 'success'}, 200
        else:
            flash(f" ❌ Error in updating movie '{new_title}'. Please Try again.", 'error')
            return {'status': 'error'}, 200
    except Exception as e:
        return f"JSON Error: {e}", 400

@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete(user_id, movie_id):
    """
    Deletes a movie from a user's favorites list.

    Args:
        user_id (int): The ID of the user.
        movie_id (int): The ID of the movie to be deleted.

    Returns:
        Response: Redirects back to the movies page with a flash message.
    """
    try:
        deleted_movie = data_manager.delete_movie(user_id, movie_id)
        redirect_url = url_for('movies', user_id=user_id)

        if deleted_movie:
            flash(f"✔️ Movie deleted!", 'success')
            return redirect(redirect_url)
        else:
            flash(f" ❌ Error in deleting movie. Please Try again.", 'error')
            return redirect(redirect_url)
    except Exception as e:
        return f"JSON Error: {e}", 400

if __name__ == '__main__':
    db.init_app(app)
    data_manager = DataManager()
    data_dir = os.path.join(basedir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    with app.app_context():
        db.create_all()

    app.run(debug=True)
