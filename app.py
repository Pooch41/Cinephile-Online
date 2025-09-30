from flask import Flask, jsonify

from data_manager import DataManager
from models import db, Movie
import os
import logging

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
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/')
def home():
    return "Welcome to Cinephile Online!"



if __name__ == '__main__':
    db.init_app(app)
    data_manager = DataManager()
    data_dir = os.path.join(basedir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    with app.app_context():
        db.create_all()

    app.run(debug=True)