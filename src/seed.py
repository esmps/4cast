"""Seed database with sample data"""

from models import User, Location, db
from app import app


db.drop_all()
db.create_all()