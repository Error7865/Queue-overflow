import unittest
from flask import current_app
from app import create_app, db


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None, msg='App is not exists.')
    
    def test_app_is_testing(self):
        self.assertTrue(self.app.config['TESTING'])