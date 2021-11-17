"""Seed database with sample data"""

from app import app
from models import db, User, Location


db.drop_all()
db.create_all()