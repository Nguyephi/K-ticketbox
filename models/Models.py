from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, TextField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired
from werkzeug.security import generate_password_hash, check_password_hash



db = SQLAlchemy()
# login config
login_manager = LoginManager()
login_manager.login_view = 'users.login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

class Rating_users (db.Model):
    __tablename__ = 'rating_users'
    rater_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), primary_key=True)
    target_user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True)
    rating = db.Column(db.Integer, nullable=False)


class Users (UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False, unique=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, unique=False)
    phone = db.Column(db.String(255), nullable=False, unique=True)
    avatar_url = db.Column(db.String, default=None)
    description = db.Column(db.String)
    birthday = db.Column(db.Date)
    gender = db.Column(db.String)
    address = db.Column(db.String)

    rater_id = db.relationship(
        'Rating_users', backref="to", primaryjoin=(id == Rating_users.rater_id))
    target_user_id = db.relationship(
        'Rating_users', backref="fro", primaryjoin=(id == Rating_users.target_user_id))

    rating_events = db.relationship('Rating_events', backref="rating_events")

    def __repr__(self):
        return """title: {}, body: {}""".format(self.username, self.email)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Rating_events (db.Model):
    __tablename__ = 'rating_events'
    rater_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey(
        'events.id'), primary_key=True)
    rating = db.Column(db.Integer, nullable=False)


class Events (db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String, nullable=False)
    user_id = db.Column(
        db.Integer,  db.ForeignKey('users.id'), nullable=False)

    users = db.relationship('Users', backref=db.backref('users'))
    rating = db.relationship('Rating_events', backref=db.backref("hello"))

    start = db.Column(db.Date, nullable=False)
    end = db.Column(db.Date)
    img_url = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    count_click = db.Column(db.Integer, nullable=False, default=0)

    count_rating =  db.Column(db.Integer, nullable=False, default=0)
    avg_rating =db.Column(db.Float, nullable=False, default=0)
    
    isprivate = db.Column(db.Boolean, default=False)
    isDelete = db.Column(db.Boolean, default=False)

class Tickets (db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(
        db.Integer,  db.ForeignKey('events.id'), nullable=False)
    events = db.relationship('Events', backref=db.backref("events"))
    ticket_name = db.Column(db.String, nullable=False)
    ticket_price = db.Column(db.Integer, nullable=False)
    stocks = db.Column(db.Integer, nullable=False)


class Orders (db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(
        db.Integer,  db.ForeignKey('events.id'), nullable=False)
    events = db.relationship('Events', backref=db.backref("events1"))
    user_id = db.Column(
        db.Integer,  db.ForeignKey('users.id'), nullable=False)
    users = db.relationship('Users', backref=db.backref("users1"))
    ticket_id = db.Column(
        db.Integer,  db.ForeignKey('tickets.id'), nullable=False)
    tickets = db.relationship('Tickets', backref=db.backref("tickets1"))
    
    ticket_quantity = db.Column(db.Integer, nullable=False)
    bill_amount = db.Column(db.Float, nullable=False)

class Tags (db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String, nullable=False)

class Jointag (db.Model):
    __tablename__ = 'jointag'
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(
        db.Integer,  db.ForeignKey('tags.id'), nullable=False)
    tags = db.relationship('Tags', backref=db.backref("tags"))
    event_id = db.Column(
        db.Integer,  db.ForeignKey('events.id'), nullable=False)
    events = db.relationship('Events', backref=db.backref("from_jointag"))












class All_tickets (db.Model):
    __tablename__ = 'all_tickets'
    id = db.Column(db.Integer, primary_key=True)
    orders_id = db.Column(
        db.Integer,  db.ForeignKey('orders.id'), nullable=False)
    orders = db.relationship(
        'Orders', backref=db.backref("from_all_tickets"))

    ticket_id = db.Column(
        db.Integer,  db.ForeignKey('tickets.id'), nullable=False)
    tickets = db.relationship(
        'Tickets', backref=db.backref("from_all_tickets"))

    user_id = db.Column(
        db.Integer,  db.ForeignKey('users.id'), nullable=False)
    users = db.relationship('Users', backref=db.backref("from_all_tickets"))

    event_id = db.Column(
        db.Integer,  db.ForeignKey('events.id'), nullable=False)
    events = db.relationship('Events', backref=db.backref("from_all_tickets"))

    code = db.Column(db.String, nullable=False)

    time_purchased = db.Column(db.DateTime, nullable=False)
    time_checkin = db.Column(
        db.DateTime, default=None)
        
