"""Seed database with sample data"""

from app import db
from models import User, Location


db.drop_all()
db.create_all()

user1 = User.signup(first_name="Emma", last_name="Pines", username="esmps", password="test123", home_location="Santa Clara, CA", c_or_f="c")
user2 = User.signup(first_name="Emma", last_name="Schwartz", username="test123", password="test123", home_location="Oakland, CA", c_or_f="f")

location1 = Location(user_id=1, location="Santa Clara, CA")
location2 = Location(user_id=1, location="South Lake Tahoe, CA")
location3 = Location(user_id=2, location="Oakland, CA")
location4 = Location(user_id=2, location="London")

db.session.add_all([location1, location2, location3, location4])
db.session.commit()