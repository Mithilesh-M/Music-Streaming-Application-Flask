from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import os
import uuid


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


@app.route('/', methods=['GET'])
def index():
    albums = Album.query.order_by(Album.date_created).all()
    return render_template('index.html', albums=albums)


@app.route('/Album/Create', methods=['POST', 'GET'])
def album_create():
    if request.method == 'POST':
        album_title = request.form['title']
        new_album = Album(title=album_title)
        try:
            db.session.add(new_album)
            db.session.commit()
            return redirect('/')
        except:
            return 'Issue in adding the album'
    else:
        return render_template('album-create.html')


@app.route('/Album/Delete/<int:id>', methods=['POST', 'GET'])
def album_delete(id):
    album = Album.query.get_or_404(id)
    if request.method == 'POST':
        try:
            db.session.delete(album)
            db.session.commit()
            return redirect('/')
        except:
            return 'Issue in deleting the album'
    else:
        return render_template('album-delete.html', album=album)


@app.route('/Album/Update/<int:id>', methods=['POST', 'GET'])
def album_update(id):
    album = Album.query.get_or_404(id)
    if request.method == 'POST':
        album.title = request.form['title']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Issue in updating the album'
    else:
        return render_template('album-update.html', album=album)


@app.route('/Album/Music/<int:id>', methods=['GET'])
def music_list(id):
    album = Album.query.get_or_404(id)
    musics = Music.query.filter(album.id == Music.album_id).order_by(Music.date_created).all()
    return render_template('music-list.html', musics=musics, album=album)


@app.route('/Album/Music/Create/<int:id>', methods=['POST', 'GET'])
def music_create(id):
    album = Album.query.get_or_404(id)
    if request.method == 'POST':
        music_title = request.form['title']
        music_artist = request.form['artist']
        songUUID = str(uuid.uuid1())
        new_music = Music(title=music_title, artist=music_artist, album_id=album.id, filename=(songUUID+'.mp3'))
        try:
            db.session.add(new_music)
            db.session.commit()
            song = request.files['song']
            full_filename = os.path.join(app.config['UPLOAD_FOLDER'], (songUUID+'.mp3'))
            song.save(full_filename)
            return redirect('/Album/Music/'+str(album.id))
        except:
            return 'Issue in adding the music'
    else:
        return render_template('music-create.html', album=album)


@app.route('/Album/Music/Delete/<int:id>', methods=['POST', 'GET'])
def music_delete(id):
    music = Music.query.get_or_404(id)
    album_id = music.album_id
    if request.method == 'POST':
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], music.filename))
            db.session.delete(music)
            db.session.commit()
            return redirect('/Album/Music/'+str(album_id))
        except:
            return 'Issue in deleting the music'
    else:
        return render_template('music-delete.html', music=music)


@app.route('/Album/Music/Update/<int:id>', methods=['POST', 'GET'])
def music_update(id):
    music = Music.query.get_or_404(id)
    album_id = music.album_id
    album = Album.query.get_or_404(album_id)
    if request.method == 'POST':
        music.title = request.form['title']
        music.artist = request.form['artist']
        song = request.files['song']
        if song:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], music.filename))
            songUUID = str(uuid.uuid1())
            full_filename = os.path.join(app.config['UPLOAD_FOLDER'], (songUUID + '.mp3'))
            song.save(full_filename)
            music.filename = songUUID+'.mp3'
        try:
            db.session.commit()
            return redirect('/Album/Music/'+str(album_id))
        except:
            return 'Issue in deleting the music'
    else:
        return render_template('music-update.html', music=music, album=album)


@app.route('/Album/Music/Open/<int:id>', methods=['POST', 'GET'])
def music_open(id):
    music = Music.query.get_or_404(id)
    album_id = music.album_id
    album = Album.query.get_or_404(album_id)
    song = 'music/'+ str(music.filename)
    print(song)
    return render_template('music-open.html', music=music, album=album, song=song)


@app.route('/Search', methods=['POST'])
def search():
    search_str = request.form['search']
    albums = Album.query.filter(Album.title.contains(search_str)).order_by(Album.date_created).all()
    musics = Music.query.filter(Music.title.contains(search_str)).order_by(Music.date_created).all()
    artists = Music.query.filter(Music.artist.contains(search_str)).order_by(Music.date_created).all()
    return render_template('music-search.html', albums=albums, musics=musics, artists=artists, string=search_str)


if __name__ == "__main__":
    app.run(debug=True)
