import unittest
import json
from base64 import b64encode
from flask import url_for
from app import create_app
from app.models import User, db, Role, Comment, Post

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client=self.app.test_client()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic '+b64encode((username+':'+password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def test_no_auth(self):
        response=self.client.get('/api/v1/posts/', content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_posts(self):
        r=Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u=User(email='john@example.com', password='cat', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        #write a post
        response=self.client.post('/api/v1/posts/', headers=self.get_api_headers('john@example.com', 'cat'), data=json.dumps({'body': 'body of the *test blog* post'})) 
        self.assertEqual(response.status_code, 201)
        url=response.headers.get('Location')
        # url=data.get('url')
        self.assertIsNotNone(url)

        #get the new post
        response=self.client.get(url, headers=self.get_api_headers('john@example.com', 'cat'))
        self.assertEqual(response.status_code, 200)
        json_response=json.loads(response.get_data(as_text=True))
        # self.assertEqual('http://localhost'+json_response['url'], url)
        self.assertEqual(json_response['url'], url)
        self.assertEqual(json_response['body_html'],'<p>body of the <em>test blog</em> post</p>')

    def test_comment(self):
        r=Role.query.filter_by(name='User').first()
        u=User.query.get(1)     #john
        u1=User(email='reba@gmail.com', password='reba', confirmed=True, role=r)
        p=Post(body='Here a new post.')
        p.author=u
        db.session.add_all([u1,p])
        db.session.commit()
        

        #write a new comment
        # self.assertIsNotNone(User.query.filter_by(email='reba@gmail.com').first())
        response=self.client.post(f'api/v1/post/{p.id}/comment', headers=self.get_api_headers('reba@gmail.com', 'reba'), data=json.dumps({'body': 'Here a new comment'}))
        self.assertEqual(response.status_code, 201)
        url=response.headers.get('Location')
        self.assertIsNotNone(url)

        #get new comment
        response=self.client.get(url, headers=self.get_api_headers('reba@gmail.com', 'reba'))
        self.assertTrue(response.status_code==200)
        json_response=json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['url'], url)
        self.assertEqual(json_response['body'], 'Here a new comment')




        