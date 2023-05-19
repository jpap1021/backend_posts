import json
from app import app
import pytest



def test_hello():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode() == 'Enjoy this project, you need to create a token to use the apis, go to the login endpoint and create the token'

def test_login():
    client = app.test_client()
    response = client.post('/login', data=dict(username='user', password='password123'))
    assert response.status_code == 200
    assert 'token' in json.loads(response.data)

def test_login_invalid_credentials():
    client = app.test_client()
    response = client.post('/login', data=dict(username='foo', password='bar'))
    assert response.status_code == 401
    assert 'message' in json.loads(response.data)

def test_get_posts_unauthorized():
    client = app.test_client()
    response = client.get('/posts')
    assert response.status_code == 401
    assert 'message' in json.loads(response.data)

def test_get_posts_authorized():
    client = app.test_client()
    response = client.post('/login', data=dict(username='user', password='password123'))
    token = json.loads(response.data)['token']

    headers = {'Authorization': token}
    response = client.get('/posts', headers=headers)

    assert response.status_code == 200
    assert isinstance(json.loads(response.data), list)

def test_add_post_unauthorized():
    client = app.test_client()
    response = client.post('/posts', data=dict(title='test title', content='test content'))
    assert response.status_code == 401
    assert 'message' in json.loads(response.data)

def test_add_post_authorized():
    client = app.test_client()
    response = client.post('/login', data=dict(username='user', password='password123'))
    token = json.loads(response.data)['token']

    headers = {'Authorization': token}
    data = json.dumps(dict(title='test title', content='test content'))
    response = client.post('/posts', headers=headers, data=data, content_type='application/json')

    assert response.status_code == 200
    assert 'message' in json.loads(response.data)

def test_delete_post_unauthorized():
    client = app.test_client()
    response = client.delete('/posts/1')
    assert response.status_code == 401
    assert 'message' in json.loads(response.data)

def test_delete_post_nonexistent():
    client = app.test_client()
    response = client.post('/login', data=dict(username='user', password='password123'))
    token = json.loads(response.data)['token']

    headers = {'Authorization': token}
    response = client.delete('/posts/123', headers=headers)

    assert response.status_code == 404
    assert 'message' in json.loads(response.data)


def test_add_comment_unauthorized():
    client = app.test_client()
    response = client.post('/posts/1/comments', data=dict(comment='test comment'))
    assert response.status_code == 401
    assert 'message' in json.loads(response.data)

def test_add_comment_nonexistent_post():
    client = app.test_client()
    response = client.post('/login', data=dict(username='user', password='password123'))
    token = json.loads(response.data)['token']