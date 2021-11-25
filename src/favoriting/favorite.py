# Favorite Location

def extendApp_favorite(app):
    
    from app import verify_user_logged_in
    from flask import g, render_template, redirect
    from models import db, User, Location

    @app.route('/favorite/<new_location>', methods=['POST'])
    @verify_user_logged_in
    def favorite_location(new_location):
        """ Add location from favorites"""

        if g.user:
            user = User.query.get_or_404(g.user.id)
            locations = user.locations
            for location in locations:
                if new_location==location.location:
                    flash("Location already favorited", "danger")
                    return redirect('/')
            add_location = Location(user_id=user.id, location=new_location)
            db.session.add(add_location)
            db.session.commit()
            g.user.locations.append(add_location)
        return redirect('/')