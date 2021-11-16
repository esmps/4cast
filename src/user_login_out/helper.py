""" Helper functions for signing up, logging in, logging out """

CURR_USER_KEY = "curr_user"

import json
from flask import session, flash
from models import db, Location


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def fav_home_location(response, user):
    res = json.loads(response)
    home = Location(
        user_id=user.id,
        location=f'{res["location"]["name"]}, {res["location"]["region"]}'
    )
    db.session.add(home)
    return home