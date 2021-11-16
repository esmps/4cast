""" Sign up a user """

from user_login_out.helper import do_logout
from flask import g, flash, redirect

def extendApp_logout(app):

    @app.route('/logout')
    def logout():
        """Handle logout of user."""

        if g.user:
            do_logout()
            flash("Successfully logged out.", 'success')
            return redirect('/login')
        return redirect('/')