"""Location View tests.
    to run these tests, copy and paste into your terminal:
    FLASK_ENV=production python3 -m unittest tests.test_location_views
"""

import os
from unittest import TestCase
from models import db, User, Location
from sqlalchemy.exc import IntegrityError, InvalidRequestError

os.environ['DATABASE_URL'] = "postgresql:///4cast-test"

from app import app, CURR_USER_KEY

db.create_all()
app.config['WTF_CSRF_ENABLED'] = False

class LocationViewTestCase(TestCase):
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

########### SEARCH LOCATIONS ###########

    def test_search_location_loggedout(self):
        """Can user view location when signed out? """

        with self.client as c:
            resp = c.get('/weather', query_string={'q': 'Los Angeles, CA'}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Los Angeles, California", str(resp.data))
            self.assertIn("Sign up", str(resp.data))

    def test_search_location_loggedin(self):
        """Can user view location when signed in? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get('/weather', query_string={'q': 'Paris'}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Paris, Ile-de-France", str(resp.data))
            self.assertIn("Log out", str(resp.data))
            self.assertIn("Add to Favorites", str(resp.data))

    def test_search_location_loggedin_duplicate(self):
        """Can user view location when signed in and already in favorites? """

        with self.client as c:
            # Sign up with home location
            resp = c.post('/signup', data={"first_name": "First",
                                            "last_name": "Last",
                                            "username": "username123",
                                            "password": "pass123",
                                            "home_location": "San Francisco, California",
                                            "c_or_f": "f"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@username123", str(resp.data))

            # Search home location
            resp = c.get('/weather', query_string={'q': 'San Francisco, California'}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("San Francisco, California", str(resp.data))
            self.assertIn("Log out", str(resp.data))
            # Verify it is already in your favorites
            self.assertIn("Remove From Favorites", str(resp.data))
        
########### USER HOMEPAGE FAVORITE LOCATIONS ###########

    def test_homepage_locations(self):
        """Can user view homepage locations when signed in? """

        with self.client as c:
            # Sign up with home location
            resp = c.post('/signup', data={"first_name": "First",
                                            "last_name": "Last",
                                            "username": "username123",
                                            "password": "pass123",
                                            "home_location": "San Francisco, California",
                                            "c_or_f": "f"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@username123", str(resp.data))

            with c.session_transaction() as sess:
                user = User.query.filter_by(username="username123").first()
                sess[CURR_USER_KEY] = user.id
            
            loc = "Portland, OR"
            c.post(f'/favorite/{loc}', follow_redirects=True)
            loc = "Austin, TX"
            c.post(f'/favorite/{loc}', follow_redirects=True)

            resp = c.get('/', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("San Francisco, California", str(resp.data))
            self.assertIn("Portland, Oregon", str(resp.data))
            self.assertIn("Austin, Texas", str(resp.data))
            self.assertIn("Log out", str(resp.data))

    def test_homepage_locations_loggedout(self):
        """Can user view homepage locations when signed out? """

        with self.client as c:
            resp = c.get('/')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<img src="/static/images/logo.png" alt="clouds over sun" style="width: 40%; padding: 15px">', str(resp.data))

########### USER FAVORITE LOCATIONS ###########

    def test_location_favorite(self):
        """Can user favorite a location while logged in? """

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            loc = "San Jose, California"
            resp = c.post(f'/favorite/{loc}', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser", str(resp.data))
            self.assertIn("San Jose, California", str(resp.data))
            
    def test_location_favorite_unauth(self):
        """Can user favorite a location while logged out? """
        
        with self.client as c:
            loc = "San Jose, California"
            resp = c.post(f'/favorite/{loc}', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))


########### USER UNFAVORITE LOCATIONS ###########

    def test_location_unfavorite(self):
        """Can user favorite a location while logged in? """

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            # First favorite the location
            loc = "San Jose, California"
            resp = c.post(f'/favorite/{loc}', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("San Jose, California", str(resp.data))

            faved_location = Location.query.filter_by(user_id=self.testuser_id, location="San Jose, California").first()
            resp = c.post(f'/unfavorite/{faved_location.id}', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("San Jose, California", str(resp.data))

    def test_location_unfavorite_unauth(self):
        """Can user favorite a location while logged out? """
        
        with self.client as c:
            resp = c.post('/unfavorite/123', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))