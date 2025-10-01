from models import db, User, Movie, FavouriteMovie
from dotenv import load_dotenv
from sqlalchemy import select
import os
import requests as r
import logging

load_dotenv()
OMDB_API_KEY = os.getenv('OMDB_API_KEY')
if OMDB_API_KEY is None:
    raise RuntimeError("Missing OMDB API key")

print()

class DataManager:
    @staticmethod
    def _make_omdb_request(movie):
        try:
            raw_data = r.get(f'https://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie}', timeout=10)
            raw_data.raise_for_status()
            return raw_data.json()
        except r.exceptions.HTTPError as errh:
            logging.error(f"HTTP Error: {errh}", exc_info=True)
        except r.exceptions.RequestException as err:
            logging.error(f"Request Error: {err}", exc_info=True)
        return None

    @staticmethod
    def create_user(name: str) -> User|None:
        try:
            new_user = User(user_name=name)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except Exception as e:
            logging.error(f"Error on creating user: {e}")
            db.session.rollback()
            return None

    @staticmethod
    def get_users() -> list[dict]|None:
        query = db.select(User).order_by(User.id)
        try:
            return db.session.execute(query).scalars().all()
        except Exception as e:
            logging.error(f"Error on getting user: {e}")
            return None

    @staticmethod
    def get_movies(user_id) -> list[dict]|None:
        query = (db.Select(Movie)
                 .join(FavouriteMovie, FavouriteMovie.movie_id == Movie.id)
                 .where(FavouriteMovie.user_id == user_id)
                 .order_by(Movie.title))
        try:
            return db.session.execute(query).scalars().all()
        except Exception as e:
            logging.error(f"Error on getting user's(id: {user_id}) favourite movies: {e}")
            return None

    def add_movie(self, user_id: int, movie_title: str) -> Movie | None:
        existing_movie = db.session.execute(
            db.select(Movie).filter_by(title=movie_title)
        ).scalar_one_or_none()

        if existing_movie:
            movie_to_favourite = existing_movie
            logging.info(f"Movie '{movie_title}' already exists in DB. Linking to user {user_id}.")
        else:
            movie_data = DataManager._make_omdb_request(movie_title)

            if movie_data is None or movie_data.get('Response') == 'False':
                logging.warning(f"Failed to find movie '{movie_title}' or API request failed. User ID: {user_id}")
                return None

            movie = Movie(
                title=movie_data.get('Title'),
                director=movie_data.get('Director'),
                year_of_release=movie_data.get('Year'),
                poster_url=movie_data.get('Poster')
            )

            try:
                db.session.add(movie)
                db.session.commit()
                movie_to_favourite = movie
            except Exception as e:
                logging.warning(f"Error adding NEW movie to DB: {e}")
                db.session.rollback()
                return None

        try:
            existing_favourite = db.session.execute(
                db.select(FavouriteMovie).filter_by(
                    user_id=user_id,
                    movie_id=movie_to_favourite.id
                )
            ).scalar_one_or_none()

            if existing_favourite:
                logging.warning(f"Movie '{movie_to_favourite.title}' is already a favourite for user {user_id}.")
                return movie_to_favourite  # Return the movie object but take no action

            favourite = FavouriteMovie(
                user_id=user_id,
                movie_id=movie_to_favourite.id
            )

            db.session.add(favourite)
            db.session.commit()  # Commit the new favourite link
            return movie_to_favourite

        except Exception as e:
            logging.warning(f"Error adding favourite link for user id:{user_id}: {e}")
            db.session.rollback()
            return None
    def update_movie(self, movie_id, new_title):
        try:
            query = (db.update(Movie)
                 .where(Movie.id == movie_id)
                 .values(title = new_title))
            result = db.session.execute(query)
            if result.rowcount == 0:
                logging.warning(f"Update failed: Movie with ID {movie_id} not found.")
                db.session.rollback()
                return False
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating movie with id {movie_id}: {e}", exc_info=True)
            return False

    def delete_movie(self, user_id, movie_id):
        try:
            query = db.delete(FavouriteMovie).where(
                (FavouriteMovie.movie_id == movie_id) &
                (FavouriteMovie.user_id == user_id))
            result = db.session.execute(query)
            if result.rowcount == 0:
                logging.warning(f"Update failed: Movie with ID {movie_id} not found.")
                db.session.rollback()
                return False

            check_fav_query = db.select(FavouriteMovie).where(FavouriteMovie.movie_id == movie_id)
            is_favorited_by_others = db.session.execute(check_fav_query).first()

            if is_favorited_by_others is None:
                delete_movie_query = db.delete(Movie).where(Movie.id == movie_id)
                db.session.execute(delete_movie_query)
                logging.info(f"Movie ID {movie_id} was deleted from the Movie table.")

            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating movie with id {movie_id}: {e}", exc_info=True)
            return False

    @staticmethod
    def get_user_by_id(user_id: int):
        try:
            return db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none()
        except Exception as e:
            logging.error(f"Error on getting user ID {user_id}: {e}")
            return None