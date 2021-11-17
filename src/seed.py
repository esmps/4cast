"""Seed database with sample data"""

from app import db
from models import User, Location


db.drop_all()
db.create_all()