# View profile

def extendApp_view_profile(app):

    from flask import g, render_template
    from app import verify_user_logged_in

    @app.route('/profile')
    @verify_user_logged_in
    def view_profile():
        """ Show user profile """ 
        user = g.user
        return render_template('users/profile.html', user=user)