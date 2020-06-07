import logging
from flask import Flask, render_template, request, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user
from datetime import datetime
from passlib.hash import sha256_crypt

# Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'xDDDDsupresikretKEy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notifayy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)

# Login Handling
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# User_ID = Primary Key
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    page = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, nullable=False)
    apps_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Alert # {str(self.id)}'

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
    messenger_id = db.Column(db.String(100), nullable=True)
    telegram_id = db.Column(db.String(100), nullable=True)
    logged = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'User: {str(self.email)}'


# --------------------------------
#  -  Helping Functions for DB  -

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

# ---------------------------------------
#  -  Helping Functions for Site Walk  -

def remember_me_handle():
    if "_user_id" in session:
        if session["remember_me"]:
            app.logger.info('User was logged in - printing his site.')
            all_alerts = get_alerts()
            return render_template('index.html', alerts=all_alerts, emailuser=session['email'])
        else:
            app.logger.info('User was not logged in - printing landing page.')
            return redirect('/index.html')
    else:
        return render_template('index.html')

def get_bool(string):
    if string == "True" or string == "true":
        return True
    return False

# -----------------------
#  - Main HREF Routes  -

@app.route('/register', methods=['GET', 'POST'])
def auth():
    app.logger.info('Registration Button pressed.')
    if request.method == 'POST':

        app.logger.info('Method: POST')
        user_email = request.form['email']
        user_password = request.form['password']

        # If this returns then it means that this user exists
        user = User.query.filter_by(email=user_email).first() 

        # If user doesn't exist, redirect back
        if user: 
            flash('Email address already exists')
            app.logger.warning("Email adress already exist in the database.")
            return redirect('/')
        app.logger.info("Succesfully added new user to database.")

        # Hashing the Password
        password_hashed = sha256_crypt.hash(user_password)
        new_user = User(email=user_email, password=password_hashed)

        # Add new user to DB
        db.session.add(new_user)
        db.session.commit()

        flash('Registration went all fine! :3 You can now log in!')
        return redirect('/')
    else:
        app.logger.warning("User somehow didn't use Method: POST.")
        flash('Something went wrong with sending the registration informations.')
        return redirect('/')

@app.route('/login', methods=['POST'])
def login_post():
    app.logger.info('Login Button Pressed.')
    if request.method == 'POST':

        # Get User Informations from Form
        user_email = request.form.get('email')
        user_password = request.form.get('password')
        remember = request.form.get('remember')
        user = User.query.filter_by(email=user_email).first()

        # Checking if this user exist (doing this and pass check will throw err, if user is not in db, hence no pass)
        if not user:
            flash("There's no registered account with given email adress.")
            app.logger.warning(" User doesn't exist: " + user_email)
            return redirect('/') 

        # --- Password Check
        #     Info: I'm printing hashed version, but we actually compare the original string with hashed version in db
        pass_check = (sha256_crypt.verify(user_password, user.password))
        app.logger.info(f"Result of pass check: {pass_check} - (input: {sha256_crypt.hash(user_password)}, db: {user.password})")
        # ---

        # Verifying Password
        if not user or not pass_check:
            flash('Please check your login details and try again.')
            app.logger.warning("Wrong Credentials" + user_email)
            return redirect('/') 
        app.logger.info("Succesfully logged in user: " + user_email)
        
        # Remember Me Handling (saving in session and in param)
        login_user(user, remember=remember)
        session["remember_me"] = True if remember else False
        session["email"] = user_email
        
        # Apps Quality of Life display if already defined by user
        session["disc"] = user.discord_id
        session["mess"] = user.messenger_id
        session["tele"] = user.telegram_id
        if user.discord_id == None:
            session["disc"] = ""
        
        if user.messenger_id == None:
            session["mess"] = ""
        if user.telegram_id == None:
            session["tele"] = ""
    
        # Getting Alerts and loading the page for this user
        return redirect('/index.html')
    else:
        return remember_me_handle()

    return redirect('/')

@app.route('/alerts', methods=['GET', 'POST'])
def alerts():
    if request.method == 'POST':
        app.logger.info('Adding New Alert.')

        # Creating App Alert
        messenger_bool = get_bool(request.form['messenger'])
        telegram_bool = get_bool(request.form['telegram'])
        discord_bool = get_bool(request.form['discord'])
        email_bool = get_bool(request.form['email'])
        new_apps_bool = Apps(discord=discord_bool, telegram=telegram_bool, messenger=messenger_bool, email=email_bool)

        # First we add the app alert, then flush to retrieve it's unique ID
        db.session.add(new_apps_bool)
        db.session.flush()

        # Creating new Alert
        alert_title = request.form['title']
        alert_page = request.form['page']
        current_user_id = session["_user_id"]
        apps_bools_id = new_apps_bool.id
        new_alert = Alert(title=alert_title, page=alert_page, user_id=current_user_id, apps_id=apps_bools_id)
        db.session.add(new_alert)
        db.session.commit()

        return redirect('/index.html')
    else:
        app.logger.info('Loading Landing Page or User Main Page.')
        return remember_me_handle()

# --------------------------------
#  - Editing / Deleting Alerts  -

@app.route('/alerts/delete/<int:id>')
def delete(id):
    app.logger.info(f'Deleting Alert with ID: {id}')
    alert = Alert.query.get_or_404(id)
    db.session.delete(alert)
    db.session.commit()
    return redirect('/index.html')

# Made the alert editing very smooth - everything is handled from mainpage
@app.route('/alerts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    app.logger.info(f'Trying to edit Alert with ID: {id}')

    # Retrieving the edited Alert from DB
    alert = Alert.query.get_or_404(id)
    apps = Apps.query.get_or_404(alert.apps_id)
    if request.method == 'POST':
        app.logger.info(f'Editing Alert with ID: {id}')

        # Receiving new inputs for this alert
        alert.title = request.form['title']
        alert.page = request.form['page']
        apps.messenger = get_bool(request.form['messenger'])
        apps.telegram = get_bool(request.form['telegram'])
        apps.discord = get_bool(request.form['discord'])
        apps.email = get_bool(request.form['email'])

        # Updating the alert in DB
        db.session.commit()
        app.logger.info(f'Edited Alert with ID: {id}')

    return redirect('/index.html')

# -----------------------------------------
#  - Linking Discord/Messenger/Telegram  -

@app.route('/discord_link', methods=['POST'])
def discord_link():
    app.logger.info(f'Trying to link discord id.')

    # Retrieving the current User info from DB
    user = User.query.get_or_404(session["_user_id"])
    if request.method == 'POST':

        # Receiving new inputs for this alert
        user.discord_id = request.form['discord_id']
        session["disc"] = user.discord_id

        # Updating the alert in DB
        db.session.commit()
        app.logger.info(f"Linked Discord for user {session['_user_id']} - id: {user.discord_id}")

    return redirect('/index.html')

@app.route('/messenger_link', methods=['POST'])
def messenger_link():
    app.logger.info(f'Trying to link messenger id.')
    user = User.query.get_or_404(session["_user_id"])
    if request.method == 'POST':
        user.messenger_id = request.form['messenger_id']
        session["mess"] = user.messenger_id
        db.session.commit()
        app.logger.info(f"Linked Messenger for user {session['_user_id']} - id: {user.messenger_id}")
    return redirect('/index.html')

@app.route('/telegram_link', methods=['POST'])
def telegram_link():
    app.logger.info(f'Trying to link telegram id.')
    user = User.query.get_or_404(session["_user_id"])
    if request.method == 'POST':
        user.telegram_id = request.form['telegram_id']
        session["tele"] = user.telegram_id
        db.session.commit()
        app.logger.info(f"Linked Telegram for user {session['_user_id']} - id: {user.telegram_id}")
    return redirect('/index.html')

# ------------------------------------
#  - HREF for Mainpage and Logout  -

@app.route('/')
def index():
    app.logger.info('Landing Page Visited.')
    return remember_me_handle()

@app.route('/index.html', methods=['GET', 'POST'])
def go_home():
    all_alerts = get_alerts()
    return render_template('index.html', alerts=all_alerts, emailuser=session['email'], discsaved=session["disc"], messsaved=session["mess"], telesaved=session["tele"])

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    app.logger.info(f"User is logging out: {session['email']}")
    logout_user()
    return redirect('/')

@app.route('/changes', methods=['GET'])
def chages():
    print(request.args.get('discordId'))
    return jsonify({"change": "change 1"})


if __name__ == "__main__":
    app.run(debug=True)

# ===== Notice Info 04-06-2020 
#   First of all, password encryption was added, so:
#   > pip install passlib (507kb, guys)
#
#   Keep in mind that expanding on existing models in DB
#   Will caues error due to unexisting columns, so:
#   Navigate to ./web (here's the app.py)
#   > python
#   > from app import db
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