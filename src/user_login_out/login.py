""" Sign up a user """

from user_login_out.helper import do_login
from forms import LoginForm
from models import User
from flask import redirect, render_template, flash

def extendApp_login(app):

    @app.route('/login', methods=["GET", "POST"])
    def login():
        """Handle user login."""

        form = LoginForm()
        if form.validate_on_submit():
            user = User.authenticate(form.username.data,
                                    form.password.data)
            if user:
                do_login(user)
                flash(f"Hello, {user.full_name()}!", "success")
                return redirect("/")
            flash("Invalid credentials.", 'danger')
        return render_template('users/login.html', form=form)