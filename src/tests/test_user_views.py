"""User View tests.
    to run these tests, copy and paste into your terminal:
    FLASK_ENV=production python3 -m unittest tests.test_user_views
"""

import os
from unittest import TestCase
from models import db, User, Location
from sqlalchemy.exc import IntegrityError, InvalidRequestError

os.environ['DATABASE_URL'] = "postgresql:///4cast-test"

from app import app, CURR_USER_KEY

db.create_all()
app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
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

########### TESTS ON USER VIEWS: SIGNUP/LOGIN ###########

    def test_signup_valid(self):
        """Does user signup route work with valid credentials?"""
        with self.client as c:
            resp = c.post('/signup', data={"first_name": "First",
                                            "last_name": "Last",
                                            "username": "username123",
                                            "password": "pass123",
                                            "home_location": "San Francisco, California",
                                            "c_or_f": "f"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@username123", str(resp.data))

            u = User.query.filter_by(username = "username123").first()
            with c.session_transaction() as sess:
                self.assertEqual(sess[CURR_USER_KEY], u.id)

    def test__signup_duplicate_username(self):
        """Does user signup route work with a duplicate username?"""
        with self.client as c:
            resp = c.post('/signup', data={"first_name": "First",
                                            "last_name": "Last",
                                            "username": "testuser",
                                            "password": "pass123",
                                            "home_location": "Oakland, California",
                                            "c_or_f": "f"})
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username already used", str(resp.data))

    def test_signup_invalid_location(self):
        """Does user signup route work with an invalid location?"""
        with self.client as c:
            resp = c.post('/signup', data={"first_name": "First",
                                            "last_name": "Last",
                                            "username": "uniqueusername",
                                            "password": "pass123",
                                            "home_location": "asdfghjk",
                                            "c_or_f": "f"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("No matching location, please try again!", str(resp.data))
    
    def test_signup_invalid_password(self):
        """Does user signup route work with a password that is too short?"""
        with self.client as c:
            resp = c.post('/signup', data={"first_name": "First",
                                            "last_name": "Last",
                                            "username": "uniqueusername",
                                            "password": "pass",
                                            "home_location": "Santa Clara, California",
                                            "c_or_f": "f"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Field must be at least 6 characters long.", str(resp.data))

    def test_login_valid(self):
        """Does user login route work with valid credentials?"""
        with self.client as c:
            resp = c.post('/login', data={"username":"testuser",
                                        "password":"testuser1"},
                                        follow_redirects=True)
            with c.session_transaction() as sess:
                self.assertEqual(sess[CURR_USER_KEY], 111)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser", str(resp.data))
            self.assertIn("Hello, Test User!", str(resp.data))

    def test_login_invalid_password(self):
        """Does user login route work with invalid password?"""
        with self.client as c:
            resp = c.post('/login', data={"username":"testuser",
                                        "password":"testuser2"})
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid credentials.", str(resp.data))

    def test_login_invalid_username(self):
        """Does user login route work with invalid username?"""
        with self.client as c:
            resp = c.post('/login', data={"username":"userdoesnotexist",
                                        "password":"testuser1"})
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid credentials.", str(resp.data))

    def test_logout(self):
        """Does user logout route work?"""
        with self.client as c:
            resp = c.post('/login', data={"username":"testuser",
                                        "password":"testuser1"},
                                        follow_redirects=True)
            resp = c.get('/logout', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Successfully logged out.", str(resp.data))

########### TESTS ON USER VIEWS: VIEW USER PROFILE ###########

    def test_profile_view(self):
        """Can user view profile?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get('/profile')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<p><b>Username: </b>testuser</p>", str(resp.data))

    def test_profile_view_loggedout(self):
        """Can user view profile when logged out?"""
        with self.client as c:

            resp = c.get('/profile', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

########### TESTS ON USER VIEWS: EDIT USER PROFILE ###########

    def test_profile_edit(self):
        """Can user edit own profile?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post('/profile/edit', data={"password": "testuser1",
                                            "username":"testuser1",
                                            "c_or_f": "f"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<p><b>Username: </b>testuser1</p>", str(resp.data))
            self.assertIn("<p><b>Home Location: </b>Sunnyvale, California</p>", str(resp.data))
            self.assertIn("<p><b>Temperature Preferences:</b> \\xcb\\x9aF</p>", str(resp.data))
            self.assertIn("Successfully updated profile!", str(resp.data))
    
    def test_profile_edit_invalid_password(self):
        """Can user edit own profile with invalid password?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            resp = c.post('/profile/edit', data={"password": "incorrect_pass",
                                            "username":"testuser3",
                                            "c_or_f": "f"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid password.", str(resp.data))

    def test_profile_edit_unauthorized(self):
        """Can user edit profile logged out?"""
        with self.client as c:
            resp = c.post('/profile/edit', data={"password": "testuser1",
                                            "username":"testuser123",
                                            "c_or_f": "c"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))
        