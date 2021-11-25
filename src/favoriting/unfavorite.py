# Unfavorite Location

def extendApp_unfavorite(app):

    from app import verify_user_logged_in
    from models import db, User, Location
    from flask import g, render_template, redirect

    @app.route('/unfavorite/<int:location_id>', methods=['POST'])
    @verify_user_logged_in
    def unfavorite_location(location_id):
        """ Remove location from favorites"""

        faved_location = Location.query.get(location_id)
        if g.user:
            user = User.query.get_or_404(g.user.id)
            locations = user.locations
            if faved_location in locations:
                g.user.locations = [location for location in locations if location != faved_location]
                db.session.delete(faved_location)
                db.session.commit()
        return redirect('/')
