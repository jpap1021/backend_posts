from flask import Flask, g, request, jsonify
import sqlite3
from functools import wraps
import jwt
from datetime import datetime, timedelta
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

app = Flask(__name__)
app.config['DATABASE'] = 'database.db'
app.config['SECRET_KEY'] = 'secret_key'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def create_table():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    ''')
    db.commit()


@app.before_request
def before_request_func():
    create_table()

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token no proporcionado'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            g.user = data['username']
        except ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401

        return f(*args, **kwargs)

    return decorated

def check_auth(username, password):
    return username == 'user' and password == 'password123'

@app.route('/')
def hello():
    return 'Enjoy this project, you need to create a token to use the apis, go to the login endpoint and create the token'

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if check_auth(username, password):
        token = jwt.encode({'username': username, 'exp': datetime.utcnow() + timedelta(minutes=30)},
                           app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})

    return jsonify({'message': 'Credenciales inválidas'}), 401

@app.route('/posts', methods=['GET'])
@requires_auth
def get_posts():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()

    posts_list = []
    for post in posts:
        post_dict = {'id': post[0], 'title': post[1], 'content': post[2]}
        posts_list.append(post_dict)

    return jsonify(posts_list)

@app.route('/posts', methods=['POST'])
@requires_auth
def add_post():
    title = request.json.get('title')
    content = request.json.get('content')

    if not title or not content:
        return jsonify({'message': 'Falta el título o el contenido del post'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
    db.commit()

    return jsonify({'message': 'Post agregado exitosamente'})

@app.route('/posts/<int:post_id>', methods=['DELETE'])
@requires_auth
def delete_post(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = cursor.fetchone()

    if not post:
        return jsonify({'message': 'El post no existe'}), 404

    cursor.execute("DELETE FROM posts WHERE id=?", (post_id,))
    db.commit()

    return jsonify({'message': 'Post eliminado exitosamente'})

@app.route('/posts/<int:post_id>/comments', methods=['POST'])
@requires_auth
def add_comment(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = cursor.fetchone()

    if not post:
        return jsonify({'message': 'El post no existe'}), 404

    comment = request.json.get('comment')

    if not comment:
        return jsonify({'message': 'Falta el comentario'}), 400

    cursor.execute("INSERT INTO comments (post_id, comment) VALUES (?, ?)", (post_id, comment))
    db.commit()

    return jsonify({'message': 'Comentario agregado exitosamente'})

@app.route('/posts/<int:post_id>/comments', methods=['GET'])
@requires_auth
def get_comments(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = cursor.fetchone()

    if not post:
        return jsonify({'message': 'El post no existe'}), 404

    cursor.execute("SELECT * FROM comments WHERE post_id=?", (post_id,))
    comments = cursor.fetchall()

    comments_list = []
    for comment in comments:
        comment_dict = {'id': comment[0], 'comment': comment[2]}
        comments_list.append(comment_dict)

    return jsonify(comments_list)