"""Seed database with sample data"""

from app import db
from models import User, Location


db.drop_all()
db.create_all()

user1 = User.signup(first_name="Emma", last_name="Pines", email="emma.pines.s@gmail.com", password="test123", home_location="Santa Clara, CA", daily_emails=True)
user2 = User.signup(first_name="Emma", last_name="Schwartz", email="test@test.com", password="test123", home_location="Oakland, CA", daily_emails=False)

location1 = Location(user_id=1, location="San Francisco, CA")
location2 = Location(user_id=1, location="South Lake Tahoe, CA")
location3 = Location(user_id=2, location="Austin, TX")
location4 = Location(user_id=2, location="London")

db.session.add_all([location1, location2, location3, location4])
db.session.commit()