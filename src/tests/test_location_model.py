""" Location model tests.
    To run these tests, copy and paste into your terminal:
    python3 -m unittest tests.test_location_model
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

class LocationModelTestCase(TestCase):
    """Test Location model."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("Test_First", "Test_Last", "test_username", "password", "San Jose, CA", "c")
        u1.id = 111

        db.session.commit()

        u1 = User.query.get(u1.id)

        self.u1 = u1
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

########### TESTS ON LOCATION MODEL ###########

    def test_location_model(self):
        """ Create a new location """
        
        location = Location(user_id=self.u1.id, location="New York, New York")
        db.session.add(location)
        db.session.commit()

        self.assertEqual(len(self.u1.locations), 1)
        self.assertEqual(self.u1.locations[0], location)
        self.assertEqual(self.u1.locations[0].location, "New York, New York")