from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'music')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    date_created = db.Column(db.DateTime,  default=datetime.now(pytz.timezone('Asia/Kolkata')))

    def __repr__(self):
        return self.title


class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    artist = db.Column(db.String(300))
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
    filename = db.Column(db.String(300))
    date_created = db.Column(db.DateTime,  default=datetime.now(pytz.timezone('Asia/Kolkata')))

    def __repr__(self):
        return self.title


if __name__ == "__main__":
    app.run(debug=True)
