from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """
    Represents a user in the movie management application.

    Attributes:
        id (int): Primary key.
        user_name (str): The name of the user.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"id: {self.id} name: {self.user_name}"

    def __str__(self):
        return f"User name {self.user_name}(ID {self.id})"


class Movie(db.Model):
    """
    Represents a movie, typically sourced from an external API (like OMDb).

    Attributes:
        id (int): Primary key.
        title (str): The movie's title.
        director (str): The movie's director.
        year_of_release (int): The movie's release year.
        poster_url (str): URL to the movie poster image.
    """
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
    """
    Represents the many-to-many relationship linking Users and Movies.
    Defines which movies a specific user has favorited.

    Attributes:
        user_id (int): Foreign key to the User table (part of composite key).
        movie_id (int): Foreign key to the Movie table (part of composite key).
    """
    __tablename__ = 'user_favourite_movies'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True)
