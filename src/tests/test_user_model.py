""" User model tests.
    To run these tests, copy and paste into your terminal:
    python3 -m unittest tests.test_user_model
"""

import os
from unittest import TestCase
from models import db, User, Location
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from app import app
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('TEST_DATABASE_URL')

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("Test_First", "Test_Last", "test_username", "password", "San Jose, CA", "c")
        u2 = User.signup("Test_First2", "Test_Last2", "test_username2", "password!", "San Francisco, CA", "f")
        u1.id = 111
        u2.id = 222

        db.session.commit()

        u1 = User.query.get(u1.id)
        u2 = User.query.get(u2.id)

        self.u1 = u1
        self.uid1 = u1.id
        self.u2 = u2
        self.uid2 = u2.id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    

########### TESTS ON USER MODEL ###########

    def test_user_model(self):
        """Test basic user model works"""

        u = User(
            first_name="First",
            last_name="Last",
            username="testuser",
            password="password123",
            home_location="Los Angeles",
            c_or_f="c"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(len(u.locations), 0)
    
    def test_user_favorites(self):
        """Test user favorite locations works"""

        location1 = Location(user_id=self.u1.id, location="San Diego, CA")
        location2 = Location(user_id=self.u2.id, location="San Diego, CA")
        location3 = Location(user_id=self.u2.id, location="Oakland, CA")

        db.session.add_all([location1, location2])
        db.session.commit()

        self.u1.locations.append(location1)
        self.u2.locations.append(location2)
        self.u2.locations.append(location3)
        db.session.commit()

        self.assertEqual(len(self.u1.locations), 1)
        self.assertEqual(len(self.u2.locations), 2)
        self.assertIn("San Diego, CA", self.u1.locations[0].location)
        self.assertIn("San Diego, CA", self.u2.locations[0].location)
        self.assertIn("Oakland, CA", self.u2.locations[1].location)

########### TESTS ON USER MODEL: SIGN UP ###########

    def test_user_signup(self):
        """ Test for valid user signup"""

        user = User.signup("First", "Last", "username", "password", "New York, NY", "f")
        user.id = 333
        db.session.commit()

        user = User.query.get(user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, "First")
        self.assertEqual(user.last_name, "Last")
        self.assertEqual(user.username, "username")
        self.assertNotEqual(user.password, "password")
        self.assertTrue(user.password.startswith("$2b$"))
        self.assertEqual(user.home_location, "New York, NY")
        self.assertEqual(user.c_or_f, "f")

    def test_invalid_username(self):
        """ Test for invalid username signup"""

        # Duplicate username
        user = User.signup("John", "Smith", "test_username", "password", "San Jose, CA", "c")
        self.assertRaises(IntegrityError, db.session.commit)

    def test_invalid_location(self):
        """ Test for invalid location signup"""

        # No location given
        user = User.signup("John", "Smith", "username", "password", None, "c")
        self.assertRaises(IntegrityError, db.session.commit)

    def test_invalid_password(self):
        """ Test for invalid password signup"""

        # Password as None
        with self.assertRaises(ValueError):
            User.signup("John", "Smith", "username", None, "San Jose, CA", "c")
        
        # Password as empty string
        with self.assertRaises(ValueError):
            User.signup("John", "Smith", "username", "", "San Jose, CA", "c")

########### TESTS ON USER MODEL: AUTHENTICATION ###########

    def test_user_login(self):
        """ Test for valid user login"""

        user = User.authenticate("test_username", "password")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "test_username")
        self.assertEqual(user.full_name(), "Test_First Test_Last")
        
        user = User.authenticate("test_username2", "password!")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "test_username2")
        self.assertEqual(user.full_name(), "Test_First2 Test_Last2")
    
    def test_invalid_login(self):
        """ Tests for invalid user login"""

        # Correct password, incorrect username
        user = User.authenticate("testusername", "password")
        self.assertFalse(user)

        # Correct username, incorrect password
        user = User.authenticate("test_username", "badpassword")
        self.assertFalse(user)