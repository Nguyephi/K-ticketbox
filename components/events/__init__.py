import os
from math import floor
import string
import random
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
from components.events.forms.forms import AddEventForm, TicketForm, OrderTickets
from models.Models import db, Events, Rating_events, Tickets, Orders, All_tickets, Rating_users, Tags, Jointag
from flask_qrcode import QRcode


qrcode = QRcode()
events_blueprint = Blueprint('events', __name__,
                             template_folder='templates')


def randomStringDigits(stringLength=10):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


@events_blueprint.route('/create', methods=['post', 'get'])
@login_required
def create_event():
    form = AddEventForm()
    tags = Tags.query.all()
    group_list = [(i.id,i.tag) for i in tags]
    form.tags.choices = group_list
    if form.validate():
        new_event = Events(event=form.event.data, description=form.description.data, location=form.location.data,
                           img_url=form.img_url.data, start=form.start.data, end=form.end.data, user_id=current_user.id, isprivate=False)
        db.session.add(new_event)
        db.session.commit()
        
        for j in form.tags.data:
            new_tag = Jointag(event_id=new_event.id, tag_id = j)
            db.session.add(new_tag)
            db.session.commit()
          
        return redirect('/')
    return render_template('create.html', form=form)


@events_blueprint.route('/')
def view_events(): 
    events = Events.query.with_entities(Events).filter(Events.start > datetime.now(),Events.isDelete==False).order_by(Events.avg_rating.desc()).all()
    group = [(Tickets.query.with_entities(func.sum(Tickets.stocks).label(  # total ticket
        'total')).filter(Tickets.event_id == i.id).first()[0],
        All_tickets.query.filter_by(event_id=i.id).count())  # sold
        for i in events]
    group_tags = [ Jointag.query.filter_by(event_id=j.id).all() for j in events]
    return render_template('events.html', events=events, group=group, group_tags=group_tags)

@events_blueprint.route('/sort/<tag>')
def view_sort_events(tag): 
    events = Events.query.join(Jointag.events).filter(Jointag.tag_id==tag, Events.start > datetime.now(),Events.isDelete==False).order_by(Events.start.asc()).all()
    group = [(Tickets.query.with_entities(func.sum(Tickets.stocks).label(  # total ticket
        'total')).filter(Tickets.event_id == i.id).first()[0],
        All_tickets.query.filter_by(event_id=i.id).count())  # sold
        for i in events]
    group_tags = [ Jointag.query.filter_by(event_id=j.id).all() for j in events]
    return render_template('events.html', events=events, group=group, group_tags=group_tags)


@events_blueprint.route('/edit/<event_id>', methods=['post', 'get'])
@login_required
def edit_event(event_id):

    event = Events.query.filter_by(id=event_id, isDelete=False).first()
    event_tags = Jointag.query.filter_by(event_id=event_id).all()
    tags = Tags.query.all()
    group_list = [(i.id , i.tag) for i in tags]

    if not event or current_user.id != event.user_id:
        flash("invalid link")
        return redirect(url_for('users.renderDashboard'))
    form = AddEventForm()
    form.event.data = event.event
    form.description.data = event.description
    form.start.data = event.start

    form.img_url.data = event.img_url
    form.location.data = event.location
    form.tags.choices=group_list

    if form.validate():
        form = AddEventForm()
        event.event = form.event.data
        event.description = form.description.data
        event.start = form.start.data
        event.end = form.end.data
        event.img_url = form.img_url.data
        event.location = form.location.data
        db.session.commit()

        for j in form.tags.data:
          check_tag = Jointag.query.filter_by(event_id=event.id, tag_id=j).first()
          if not check_tag:
            new_tag = Jointag(event_id=event.id, tag_id = j)
            db.session.add(new_tag)
            db.session.commit()
          
        return redirect(url_for('users.dashboardEvents'))
    return render_template('edit_event.html', form=form, event=event, event_tags=event_tags)


@events_blueprint.route('/delete/<event_id>', methods=['post', 'get'])
@login_required
def delete_event(event_id):
    event = Events.query.filter_by(id=event_id).first()
    return render_template('confirm_delete.html', event=event)


@events_blueprint.route('/confirmdelete/<event_id>', methods=['post', 'get'])
@login_required
def confirmdelete_event(event_id):
    event = Events.query.filter_by(id=event_id).first()
    event.isDelete = True
    db.session.commit()
    return redirect(url_for('users.dashboardEvents'))
    # return redirect(url_for('users.dashboardEvents'))


@events_blueprint.route('/<event_id>')
def view_event(event_id):
    event = Events.query.filter_by(id=event_id, isDelete=False).first()
    if not event:
        flash("This event is not available")

    count_user_rating = Rating_users.query.filter_by(
        target_user_id=event.user_id).count()
    if count_user_rating == 0:
        avg_user_rating = 0

    else:
        avg_user_rating = Rating_users.query.with_entities(func.sum(Rating_users.rating).label(
            'total')).filter(Rating_users.target_user_id == event.user_id).first()[0]/count_user_rating

    # query from rating_events or events table are oke !
    count_rater = Rating_events.query.filter_by(event_id=event_id).count()

    if count_rater == 0:
        avg_rate = 0
    else:
        avg_rate = Rating_events.query.with_entities(func.sum(Rating_events.rating).label(
            'total')).filter(Rating_events.event_id == event_id).first()[0]/count_rater
    if not current_user.is_authenticated:
        check = None
    else:
        check = Rating_events.query.filter_by(
            rater_id=current_user.id, event_id=event_id).first()

    ticket_price = Tickets.query.filter_by(event_id=event_id).order_by(
        Tickets.ticket_price.asc()).first()
    if ticket_price:
        total_quantity = Tickets.query.with_entities(func.sum(Tickets.stocks).label(
            'total')).filter(Tickets.event_id == event_id).first()[0]
        sold_quantity = All_tickets.query.filter_by(event_id=event_id).count()
        remaining_ticket = total_quantity - sold_quantity
    else: 
        total_quantity = 0
        sold_quantity = 0
        remaining_ticket = -1
    return render_template('view_event.html',
                           event=event,
                           check=check,
                           count_rater=count_rater,
                           avg_rate=avg_rate,
                           ticket_price=ticket_price,
                           count_user_rating=count_user_rating,
                           avg_user_rating=avg_user_rating,
                           total_quantity=total_quantity,
                           remaining_ticket=remaining_ticket)


@events_blueprint.route('/rate_event/<event_id>/<value>', methods=['post', 'get'])
@login_required
def rate_event(event_id, value):
    event = Events.query.filter_by(id=event_id, isDelete=False).first()
    check = Rating_events.query.filter_by(
        rater_id=current_user.id, event_id=event_id).first()
    print("SDSDSDSDSDSDSDSDSDS++++++++", check)
    # check_user_rating = Rating

    if check is None:
        new_rate = Rating_events(
            rater_id=current_user.id, event_id=event_id, rating=value)
        # adding count_rating and avg_rating to table events to reduce load on render many events at onnce
        event.count_rating += 1
        count_rater = Rating_events.query.filter_by(event_id=event_id).count()
        if count_rater == 0:
            sum_rate = int(value)
        else:
            sum_rate = Rating_events.query.with_entities(func.sum(Rating_events.rating).label(
                'total')).filter(Rating_events.event_id == event_id).first()[0] + int(value)
        event.avg_rating = sum_rate / (int(count_rater) + 1)

        db.session.add(new_rate)
        db.session.commit()
        return redirect('/events/'+str(event_id))

    elif check:
        sum_rate = Rating_events.query.with_entities(func.sum(Rating_events.rating).label(
            'total')).filter(Rating_events.event_id == event_id).first()[0] - int(check.rating) + int(value)
        check.rating = value
        event.avg_rating = sum_rate / event.count_rating
        db.session.commit()
        return redirect('/events/'+str(event_id))

    return render_template('view_event.html', event=event)


@events_blueprint.route('/<event_id>/manage_tickets/', methods=['post', 'get'])
@login_required
def handle_tickets(event_id):
    event = Events.query.filter_by(id=event_id).first()
    tickets = Tickets.query.filter_by(event_id=event_id).all()
    if current_user.id != event.user_id:
        return redirect(url_for('users.renderDashboard'))
    form = TicketForm()
    if form.validate():
        new_ticket = Tickets(event_id=event_id, ticket_name=form.ticket_name.data,
                             ticket_price=form.ticket_price.data, stocks=form.stocks.data)
        db.session.add(new_ticket)
        db.session.commit()
        return redirect('/events/'+str(event_id)+'/manage_tickets/')
    return render_template('manage_tickets.html', tickets=tickets, form=form)


@events_blueprint.route('/order/<event_id>/step1/', methods=['post', 'get'])
@login_required
def order_step1(event_id):
    tickets = Tickets.query.filter_by(event_id=event_id).all()
    this_event = Events.query.filter_by(id=event_id, isDelete=False).first()

    if not this_event:
        flash("This event is not available")
#
    groups_list = [(i.id, str(i.ticket_name) + " - Price: " + '{:,}'.format(i.ticket_price) + " - Available tickets:" + str(
        int(i.stocks) - int(All_tickets.query.filter_by(ticket_id=i.id).count()))) for i in tickets]
    form = OrderTickets()
    form.ticket_type.choices = groups_list

    if form.validate():
        order_ticket = form.ticket_type.data  # ticket type id
        order_quantity = form.quantity.data
        # check stocks ticket_id means ticket type
        check_ticket = Tickets.query.filter_by(id=order_ticket).first()
        check_stocks = All_tickets.query.filter_by(
            ticket_id=order_ticket).count()
        if int(order_quantity) > (int(check_ticket.stocks) - int(check_stocks)):
            flash(
                "There's not enough available ticket, please choose another ticket type or amount of ticket.")
            return render_template('order_tickets.html', tickets=tickets, form=form)
        # end check

        selected_ticket = Tickets.query.filter_by(id=order_ticket).first()
        order_bill_amount = int(
            selected_ticket.ticket_price) * int(order_quantity)

        new_order = Orders(event_id=event_id,
                           user_id=current_user.id,
                           ticket_id=order_ticket,
                           ticket_quantity=order_quantity,
                           bill_amount=order_bill_amount)
        db.session.add(new_order)
        db.session.commit()

        for i in range(int(order_quantity)):
            new_ticket = All_tickets(orders_id=new_order.id,
                                     ticket_id=order_ticket,
                                     user_id=current_user.id,
                                     event_id=event_id,
                                     code=randomStringDigits(),
                                     time_purchased=datetime.now())
            db.session.add(new_ticket)
            db.session.commit()

        return redirect('events/order/'+str(event_id)+'/complete/'+str(new_order.id))
    return render_template('order_tickets.html', tickets=tickets, form=form)


@events_blueprint.route('/order/<event_id>/complete/<order_id>', methods=['post', 'get'])
@login_required
def order_complete(event_id, order_id):
    order = Orders.query.filter_by(
        user_id=current_user.id, event_id=event_id, id=order_id).first()
    if not order:
        flash("Invalid link")
        return redirect('/')
    if current_user.id != order.user_id:
        return redirect('/')
    s = order.users.name + str(order.id)
    tickets = All_tickets.query.filter_by(orders_id=order_id).all()
    return render_template('order_complete.html', order=order, s=s, tickets=tickets)



