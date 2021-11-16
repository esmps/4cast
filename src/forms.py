from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class UserAddForm(FlaskForm):
    """Form for adding users."""

    first_name =StringField('First Name', validators=[DataRequired()])
    last_name =StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    home_location = StringField('Home Location')
    c_or_f = SelectField('C or F', choices=[('c', 'C'), ('f', 'F')], validators=[Length(min=1, max=1)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6), DataRequired()])


class EditProfileForm(FlaskForm):
    """Form to edit user profile"""

    first_name =StringField('First Name', validators=[Optional()])
    last_name =StringField('Last Name', validators=[Optional()])
    username = StringField('Username', validators=[Optional()])
    home_location = StringField('Home Location')
    password = PasswordField('Password', validators=[DataRequired()])
    c_or_f = SelectField('C or F', choices=[('c', 'C'), ('f', 'F')], validators=[Length(min=1, max=1), Optional()])
