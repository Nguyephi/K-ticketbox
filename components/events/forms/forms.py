from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, TextField, TextAreaField, DateField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired
from flask_bootstrap import Bootstrap
from datetime import datetime, date


class AddEventForm (FlaskForm):
    event = StringField("Event name", validators=[DataRequired(), Length(
        min=0, max=255, message="Event name must be filled")])
    description = TextAreaField("Description",  validators=[DataRequired()])
    start = DateField("Starting date", format='%m/%d/%Y',validators=[DataRequired("Please enter the event starting Date in mm/dd/yyy.")])
    end = DateField("Ending date", format='%m/%d/%Y',validators=[DataRequired("Please enter the event ending Date in mm/dd/yyy.")])
    img_url = StringField("img url", validators=[DataRequired(), Length(
        min=0, max=255, message="img url must be filled")])
    location = StringField("location", validators=[DataRequired(), Length(
        min=0, max=255, message="Event location must be filled")])

        
    tags = SelectMultipleField("Select tags",  coerce=int, option_widget=True)

    submit = SubmitField("Submit this event")
    def validate_start(self, field):
        if field.data < date.today():
            raise ValidationError("Date of event must be a future date")
    def validate_end(self, field):
        if field.data < self.start.data:
            raise ValidationError("End Date of event must be after start date")




class TicketForm (FlaskForm):
    ticket_name = StringField("Ticket name (type)", validators=[DataRequired(), Length(
        min=0, max=255, message="Ticket name must be filled")])

    ticket_price = StringField("Ticket price",  validators=[DataRequired()])

    stocks = StringField("Quantity",  validators=[DataRequired()])

    submit = SubmitField("Update Ticket")


class OrderTickets (FlaskForm):
    ticket_type = SelectField(
        'Select Ticket', coerce=int, validators=[InputRequired()])

    quantity = StringField("Quantity", validators=[DataRequired()])
    submit = SubmitField("Next step")

