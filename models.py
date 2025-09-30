from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base, sessionmaker

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"id-{self.id} name - {self.user_name}"

    def __str__(self):
        return f"User name {self.user_name}(ID {self.id})"

class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    director = db.Column(db.String)
    year_of_release = db.Column(db.Integer)
    poster_url = db.Column(db.String)

    def __repr__(self):
        return (f"id-{self.id} title - {self.title} dir - {self.director} "
                f"yor - {self.year_of_release} poster - {self.poster_url}")

    def __str__(self):
        return (f"Movie: {self.title}(ID {self.id} {self.year_of_release}) "
                f"directed by {self.director} \n(Poster URL {self.poster_url})")

class FavouriteMovie(db.Model):
    __tablename__ = 'user_favourite_movies'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'),  primary_key=True)




