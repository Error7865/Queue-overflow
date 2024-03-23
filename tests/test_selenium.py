# Here selenium work pefectly I tested in isolation but I think I don't know how to start that app and test the route 

import unittest
import threading
import re 
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from app import create_app, db
from app.models import Role, User
from app.fake import users, posts


class SeleniumTestCase(unittest.TestCase):
    client=None
    @classmethod
    def setUpClass(cls) -> None:
        #start edge browser
        options=webdriver.EdgeOptions()
        options.add_argument('headless')
        try:
            cls.client=webdriver.Edge(options=options)
            # cls.client=webdriver.Edge()
        except:
            pass

        #skip these tests if the browser could not started
        if cls.client:
            #create the application
            cls.app=create_app('testing')
            cls.app_context=cls.app.app_context()
            cls.app_context.push()

            #support logging to keep unittest output clean
            import logging
            logger=logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            #create the database and populate with some fake data 
            db.create_all()
            Role.insert_roles()
            users(10)
            posts(10)

            #add an administrator user
            admin_role=Role.query.filter_by(name='Administrator').first()
            admin=User(email='john@example.com', username='John', password='cat', role=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()

            #start new flask server in a thread
            cls.server_thread=threading.Thread(target=cls.app.run, kwargs={'debug': False})
            cls.server_thread.start()

            # give the server a second to ensure it is up 
            time.sleep(1)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.client:
            #stop the flask server and the browser
            cls.client.get('http://localhost:5000/main/shutdown')
            cls.client.quit()
            cls.server_thread.join()

            #destroy database
            db.drop_all()
            db.session.remove()

            #remove applicataion context
            cls.app_context.pop()

    def setUp(self) -> None:
        if not self.client:
            self.skipTest('Browser not available.')

    def tearDown(self) -> None:
        pass

    def test_admin_home_page(self):
        # navigate to home page 
        self.client.get('http://locathost:500/main/')
        self.assertTrue(re.search(r'Hello,\sStranger!', self.client.page_source))

        # navigate to Login Page 
        self.client.find_element(By.LINK_TEXT, 'Log In').click()
        self.assertIn('<h1>Login</h1>', self.client.page_source)

        # login 
        self.client.find_element(By.NAME, 'email').send_keys('john@example.com')
        self.client.find_element(By.NAME, 'password').send_keys('cat')
        self.client.find_element(By.NAME, 'submit').click()
        self.assertTrue(re.search(r'Hello,\sJohn!', self.client.page_source))

        # navigate to user's profile 
        self.client.find_element(By.LINK_TEXT, 'Profile').click()
        self.assertIn('<h1>John', self.client.page_source)
