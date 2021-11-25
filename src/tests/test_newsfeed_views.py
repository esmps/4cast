"""Newsfeed View tests.
    to run these tests, copy and paste into your terminal:
    FLASK_ENV=production python3 -m unittest tests.test_newsfeed_views
"""

import os
from unittest import TestCase
from models import db, User, Location
from sqlalchemy.exc import IntegrityError, InvalidRequestError

os.environ['DATABASE_URL'] = "postgresql:///4cast-test"

from app import app, CURR_USER_KEY

db.create_all()
app.config['WTF_CSRF_ENABLED'] = False

class NewsfeedViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(first_name="Test",
                                    last_name="User",
                                    username="testuser",
                                    password="testuser1",
                                    home_location="Sunnyvale, California",
                                    c_or_f="c")
        self.testuser_id = 111
        self.testuser.id = self.testuser_id
        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

########### VIEW NEWSFEED ###########

    def test_view_newsfeed_loggedout(self):
        """ Can user view newsfeed logged out? """

        with self.client as c:
            resp = c.get('/climatenews/1')
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sign up", str(resp.data))
            self.assertIn("Climate News", str(resp.data))
            self.assertIn('<p class="text-center"><small>Powered by <a href="https://newsapi.org" title="Free News API">News API</small></a></p>', str(resp.data))

    def test_view_newsfeed_loggedin(self):
        """ Can user view newsfeed logged in? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            resp = c.get('/climatenews/1')
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Log out", str(resp.data))
            self.assertIn("Climate News", str(resp.data))
            self.assertIn('<p class="text-center"><small>Powered by <a href="https://newsapi.org" title="Free News API">News API</small></a></p>', str(resp.data))
