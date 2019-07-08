import os
from flask import Flask, request, render_template, abort, redirect, url_for, flash, Blueprint
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, TextField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired
from flask_bootstrap import Bootstrap
from components.users import users_blueprint
from components.events import events_blueprint,qrcode
from models.Models import db, Users, login_manager
from flask_qrcode import QRcode # [...] QRcode(app) # [...]
from flask_wtf.csrf import CsrfProtect




app = Flask(__name__)
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
CsrfProtect(app)
db.init_app(app)
auth = Blueprint('auth', __name__)
migrate = Migrate(app, db, compare_type=True)
##################################
bootstrap = Bootstrap(app)
qrcode.init_app(app)

login_manager.init_app(app)

#using postgres
POSTGRES = {
    'user': os.environ['POSTGRES_USER'],
    'pw': os.environ['POSTGRES_PWD'],
    'db': os.environ['POSTGRES_DB'],
    'host': os.environ['POSTGRES_HOST'],
    'port': os.environ['POSTGRES_PORT'],
}

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:\
%(port)s/%(db)s' % POSTGRES
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# create db






#INDEX
@app.route("/")
def index():
    return redirect('/events')

#USERs
app.register_blueprint(users_blueprint, url_prefix='/users')

#EVENTs
app.register_blueprint(events_blueprint, url_prefix='/events')


#autorun
if __name__ == '__main__':
    app.run(debug=True)
    print("this is the main")
    
