# View profile

from flask import g, render_template

def extendApp_view_profile(app):

    from app import verify_user_logged_in

    @verify_user_logged_in
    @app.route('/profile')
    def view_profile():
        """ Show user profile """ 
        user = g.user
        return render_template('users/profile.html', user=user)