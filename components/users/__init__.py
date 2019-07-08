import os
from flask import Flask, request, render_template, abort, redirect, url_for, flash, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, TextField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired
from flask_bootstrap import Bootstrap
from models.Models import db, Users, Rating_users, login_manager, Events, Orders
from components.users.forms.forms import RegistrationForm, LoginForm, UpdateProfile

# login_manager.login_view = 'login'



users_blueprint = Blueprint('users', __name__,
                            template_folder='templates')

@users_blueprint.route('/signup', methods=['post','get'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = Users(username=form.username.data, email=form.email.data, phone=form.phone.data, password=form.password.data, name=form.name.data )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect ('/')
    return render_template('signup.html', form=form)

@users_blueprint.route('/login', methods=['post','get'])
def login():
    form = LoginForm()
    if form.validate_on_submit():        
        log_user = Users.query.filter_by(username=form.username.data).first()
        if log_user is None:
            return redirect(url_for('users.signup'))
        if not log_user.check_password(form.password.data):
            return redirect(url_for('users.login'))

        login_user(log_user)

        return redirect('../events')
    return render_template('login.html', form=form)


@users_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect('../')

@users_blueprint.route('/vote/<target_id>/<rating>/<event_id>')
def voteuser(target_id,rating,event_id): 
    check_user_rating = Rating_users.query.filter_by(rater_id=current_user.id, target_user_id = target_id).first()
    if not check_user_rating :    
        user_1 = Users.query.filter_by(id=current_user.id).first()
        user_2 = Users.query.filter_by(id=target_id).first()

        rate = Rating_users(rating=rating)
        rate.target_user_id = user_2.id
        user_1.rater_id.append(rate)
        db.session.commit()
    else:
        check_user_rating.rating = rating
        db.session.commit()

    return redirect(url_for('events.view_event', event_id=event_id))

@users_blueprint.route('/whovoteme')
def showvoteme():
    user_1 = Users.query.filter_by(id=1).first()
    print("&^*&^%*ABJSGAKJSGAJSAS", user_1)
    print("&^*&^%*ABJSGAKJSGAJSAS", user_1.rater_id[0].fro.username)
    return user_1.rater_id[0].fro.username
    

@users_blueprint.route('/voted')
def showvoted():
    user_1 = Users.query.filter_by(id=2).first()
    print("&^*&^%*ABJSGAKJSGAJSAS", user_1)
    print("&^*&^%*ABJSGAKJSGAJSAS", user_1.target_user_id[0].to.username)
    return user_1.target_user_id[0].to.username
    


@users_blueprint.route('/dashboard')
def renderDashboard():
    return render_template('dashboard_welcome.html')

@users_blueprint.route('/dashboard/profile')
def dashboardProfile():
    user = Users.query.filter_by(id=current_user.id).first()
    return render_template('dashboard_profile.html', user=user)

@users_blueprint.route('/dashboard/ordershistory')
def dashboardOrders():
    orders = Orders.query.filter_by(user_id=current_user.id).order_by(Orders.id.desc()).all()
    return render_template('dashboard_orders.html', orders=orders)

@users_blueprint.route('/dashboard/eventshosted')
def dashboardEvents():
    events = Events.query.filter_by(user_id=current_user.id, isDelete=False).order_by(Events.id.desc()).all()
    return render_template('dashboard_events.html', events=events)

@users_blueprint.route('/dashboard/updateprofile', methods=['post','get'])
def updateProfile():
    user = Users.query.filter_by(id=current_user.id).first()
    form = UpdateProfile()
    form.gender.data = user.gender
    form.avatar_url.data = user.avatar_url
    form.birthday.data = user.birthday
    form.description.data = user.description
    form.address.data = user.address

    if request.method == 'POST':
        form = UpdateProfile()
        if form.validate():
            form = UpdateProfile()
            user.gender = form.gender.data
            user.birthday = form.birthday.data
            user.description = form.description.data
            user.address = form.address.data
            user.avatar_url = form.avatar_url.data
            db.session.commit()
        return render_template('dashboard_profile.html', user=user)
    return render_template('dashboard_updateprofile.html', user=user, form=form)

@users_blueprint.route('/dashboard/seller')
def dashboard_seller():
    return render_template('dashboard_seller.html')


## user => all ticket sold:
## from orders => filter Orders.events.user_id == current_user.id  >sum(ticket_quantity) or sum(bill_amount)