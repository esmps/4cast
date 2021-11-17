from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class UserAddForm(FlaskForm):
    """Form for adding users."""

    first_name =StringField('First Name', validators=[DataRequired()])
    last_name =StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    home_location = StringField('Home Location', validators=[DataRequired()])
    c_or_f = SelectField('C or F', choices=[('c', 'C'), ('f', 'F')], validators=[Length(min=1, max=1)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class EditProfileForm(FlaskForm):
    """Form to edit user profile"""

    first_name =StringField('First Name', validators=[Optional()])
    last_name =StringField('Last Name', validators=[Optional()])
    username = StringField('Username', validators=[Optional(), Length(min=3)])
    home_location = StringField('Home Location', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired()])
    c_or_f = SelectField('C or F', choices=[('c', 'C'), ('f', 'F')], validators=[Length(min=1, max=1), Optional()])
