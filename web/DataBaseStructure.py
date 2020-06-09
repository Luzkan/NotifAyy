import logging
from flask import Flask, render_template, request, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user
from datetime import datetime
from passlib.hash import sha256_crypt

# -------------------------
#  -  Database Structure -

#   ALERT TABLE
# +----+-------------+-----------------+-------------------+---------------+---------------+
# | ID | TITLE (str) |   PAGE (url)    | DATE_ADDED (date) | USER_ID (key) | APPS_ID (key) |
# +----+-------------+-----------------+-------------------+---------------+---------------+
# |  1 | My Site     | http://site.com | 07.06.2020        | 2             | 4             |
# |  2 | (...)       | (...)           | (...)             | (...)         | (...)         |
# +----+-------------+-----------------+-------------------+---------------+---------------+
#   > APPS_ID -> Key, which is:   Primary Key in APPS Table
#   > USER_ID -> Key, which is:   Primary Key in USER Table


#   APPS TABLE
# +----+----------------+-----------------+------------------+--------------+
# | ID | Discord (bool) | Telegram (bool) | Messenger (bool) | Email (bool) |
# +----+----------------+-----------------+------------------+--------------+
# |  4 | true           | false           | true             | true         |
# |  5 | (...)          | (...)           | (...)            | (...)        |
# +----+----------------+-----------------+------------------+--------------+
#   > ID -> Primary Key, which is:    Referenced by ALERTS TABLE (APPS_ID)


#   USER TABLE
# +----+----------------+-----------------------+------------------+--------------------+--------------+
# | ID |  Email (str)   | Passowrd (str hashed) | Discord_Id (int) | Messenger_Id (str) | Logged (int) |
# +----+----------------+-----------------------+------------------+--------------------+--------------+
# |  2 | cool@gmail.com | <hash>                | 21842147         | ???                | 1            |
# |  3 | (...)          | (...)                 | (...)            | (...)              |              |
# +----+----------------+-----------------------+------------------+--------------------+--------------+
#   > ID -> Primary Key, which is:    Referenced by ALERTS TABLE (USER_ID)

# -------------------------------
#  -  Database Classes Tables  -
app = Flask(__name__)
app.config['SECRET_KEY'] = 'xDDDDsupresikretKEy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notifayy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)

# Login Handling
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    page = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, nullable=False)
    apps_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Alert # {str(self.id)}'


class ChangesForDiscord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'ChangesForDiscord # {str(self.id)}'

class Apps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord = db.Column(db.Boolean, nullable=False, default=False)
    telegram = db.Column(db.Boolean, nullable=False, default=False)
    messenger = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'Apps # {str(self.id)}. Status (d/t/m): ({str(self.discord)}/{str(self.telegram)}/{str(self.messenger)}/{str(self.email)})'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    discord_id = db.Column(db.Integer, nullable=True)

    messenger_l = db.Column(db.String(100), nullable=True)
    messenger_token = db.Column(db.String(100), nullable=True)
    telegram_id = db.Column(db.String(100), nullable=True)
    logged = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'User: {str(self.email)}'

 

# User_ID = Primary Key
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_items_for_messaging(id):
    a=Alert.query.filter_by(id=id).first()
    u=User.query.filter_by(id=a.user_id)
    bools=Apps.query.filter_by(id=id)
    return [a,u,bools]
def add_to_changes(item):
    item=ChangesForDiscord(alert_id=item[0],content=item[1])
    db.session.add(item)
    db.session.commit()

# --------------------------------
#  -  Helping Functions for DB  -

def get_everything(alert_id):
    al=Alert.query.filter_by(id=alert_id).first()
    user=User.query.filter_by(id=al.user_id).first()
    apps=Apps.query.filter_by(id=al.apps_id).first()
    return al, user, apps

def allAlerts():
    return Alert.query.all()
    
    
def get_alerts():
    # Getting current User ID and retrieving his alerts
    cur_user_id = session["_user_id"]
    all_alerts = Alert.query.filter_by(user_id=cur_user_id).order_by(Alert.date_added).all()
    all_apps = get_apps(all_alerts)

    # Adding to Alert Object the booleans for apps through apps_id key
    for alert in all_alerts:
        alert.messenger = all_apps[alert.id].messenger
        alert.discord = all_apps[alert.id].discord
        alert.telegram = all_apps[alert.id].telegram
        alert.email = all_apps[alert.id].email

    return all_alerts

def get_alerts_by_id(discordId: str):
    all_alerts = Alert.query.filter_by(user_id=discordId).order_by(Alert.date_added).all()
    all_apps = get_apps(all_alerts)

    for alert in all_alerts:
        alert.discord = all_apps[alert.id].discord

    return all_alerts

def get_apps(all_alerts):
    all_apps = {}
    for alert in all_alerts:
        all_apps[alert.id] = Apps.query.get(alert.apps_id)
    return all_apps
    

# ===== Notice Info 04-06-2020 
#   First of all, password encryption was added, so:
#   > pip install passlib (507kb, guys)
#
#   Keep in mind that expanding on existing models in DB
#   Will caues error due to unexisting columns, so:
#   Navigate to ./web (here's the app.py)
#   > python
#   > from DataBaseStructure import db
#   > db.reflect()
#   > db.drop_all()
#   > db.create_all()

# ===== Notice Info 05-06-2020 
#   To surprass all these annoying false-positive warnings with
#   db.* and logger.*, just do this:
#   > pip install pylint-flask (10 KB)
#   Then in .vscode/settings.json (if you are using vscode), add:
#   > "python.linting.pylintArgs": ["--load-plugins", "pylint-flask"]

# ===== Notice Info 06-06-2020 
#    > app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
#    ^ This is for the FSADeprecationWarning (adds significant overhead)
#                   and will be disabled by default in the future anyway
#
#    Cleaned up this code a bit, and made it more visual and easy to read
#    Added linking functionality for all buttons, so you can do w/e you want
#    with them right now. Also added email bool for alerts    