from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, TextField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired
from flask_bootstrap import Bootstrap
from models.Models import Users


class RegistrationForm (FlaskForm):
    username = StringField("User Name", validators=[DataRequired(), Length(
        min=3, max=79, message="username should have at least 3 characters and maximum of 79 character")])
    email = StringField("Email",  [InputRequired("Please enter your email address."), Email(
        "This field requires a valid email address")])
    name = StringField("Name", validators=[DataRequired(), Length(
        min=2, max=255, message="Your name is required")])
    phone = StringField("Phone number", validators=[DataRequired(), Length(
        min=10, max=10, message="phone number should have 10 digits")])
    password = PasswordField("password", validators=[
                            DataRequired(), EqualTo("pass_confirm")])
    pass_confirm = PasswordField(
        "Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")
############################################################################################
    # CHECK VALIDATION FROM DATABASE

    def validate_username(self, field):
        if Users.query.filter_by(username=field.data).first():
            raise ValidationError("YOur username has been registered!!")

    def validate_email(self, field):
        if Users.query.filter_by(email=field.data).first():
            raise ValidationError("YOur email has been registered!!")


class LoginForm (FlaskForm):
    username = StringField("User Name")
    password = PasswordField("password")
    submit = SubmitField("Login")


class UpdateProfile (FlaskForm):
    gender = SelectField(
        'Select gender',
        choices=[('male', 'Male'), ('female', 'Female'), ('organisation', 'Organisation')])
    birthday = DateField("Birthday, in mm/dd/yyyy", format='%m/%d/%Y')
    description = TextAreaField("About me",  validators=[DataRequired()])
    address = StringField("location", validators=[DataRequired(), Length(
        min=0, max=255, message="Event location must be filled")])
    avatar_url = StringField("Avatar URL")

    submit = SubmitField("Update")

