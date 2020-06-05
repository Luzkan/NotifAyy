import logging
from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user
from datetime import datetime
from passlib.hash import sha256_crypt


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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'xDDDDsupresikretKEy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notifayy.db'
# # Info: This is for the FSADeprecationWarning (adds significant overhead)
#         and will be disabled by default in the future anyway
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# User_ID = Primary Key
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# So it's better to use "app_id" (int) that will specify a combination
# of what apps user want to be informed on. This way, we do not add more
# columns to "Alert" as more supporting apps are included to the app.
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    page = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # user_id = db.Column(db.Integer, nullable=False)
    # apps_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return 'Alert # ' + str(self.id)

class Apps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord = db.Column(db.Boolean, nullable=False, default=False)
    telegram = db.Column(db.Boolean, nullable=False, default=False)
    messenger = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'Apps # {str(self.id)}. Status (d/t/m): ({str(self.discord)}/{str(self.telegram)}/{str(self.messenger)}) '


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __repr__(self):
        return 'User: ' + str(self.email)

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
        app.logger.info('Method: NOT POST')
        all_alerts = Alert.query.order_by(Alert.date_added).all()
        all_users = User.query.order_by(User.id).all()
        return render_template('index.html', alerts=all_alerts, users=all_users)

@app.route('/login', methods=['POST'])
def login_post():
    app.logger.info('Login Button Pressed.')
    if request.method == 'POST':

        app.logger.info('Method: POST')
        user_email = request.form.get('email')
        user_password = request.form.get('password')
        remember = request.form.get('remember')

        user = User.query.filter_by(email=user_email).first()

        # --- Debugging Passwords check
        #     Info: I'm printing hashed version, but we actually
        #           compare the original string with hashed version in db
        app.logger.debug("Passwords: (input: " + sha256_crypt.hash(user_password) + ", db: " + user.password + ")")
        res = (sha256_crypt.verify(user_password, user.password))
        app.logger.debug("Result of pass check: " + str(res))
        # ---

        if not user or not (sha256_crypt.verify(user_password, user.password)):
            flash('Please check your login details and try again.')
            app.logger.warning("Wrong Credentials / User doesn't exist: " + user_email)
            return redirect('/') 

        app.logger.info("Succesfully logged in user: " + user_email)
        login_user(user, remember=remember)
        session["remember_me"] = True if remember else False
    
        all_alerts = Alert.query.order_by(Alert.date_added).all()

        # Session is a way to keep values when moving around pages
        session["email"] = user_email

        return render_template('index.html', alerts=all_alerts, emailuser=user_email)

    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def index():
    app.logger.info('Landing Page Visited.')
    if request.method == 'POST':
        app.logger.debug('Landing Page Visited with method POST')
        # Creating App Alert
        messenger_bool = get_bool(request.form['messenger'])
        telegram_bool = get_bool(request.form['telegram'])
        discord_bool = get_bool(request.form['discord'])
        new_apps_bool = Apps(discord=discord_bool, telegram=telegram_bool, messenger=messenger_bool)

        # First we add the app alert, then flush to retrieve it's unique ID
        db.session.add(new_apps_bool)
        db.session.flush()

        # Creating new Alert
        alert_title = request.form['title']
        alert_page = request.form['page']
        current_user_id = session["_user_id"]
        apps_bools_id = new_apps_bool.id
        #new_alert = Alert(title=alert_title, page=alert_page, user_id=current_user_id, apps_id=apps_bools_id)
        new_alert = Alert(title=alert_title, page=alert_page)
        db.session.add(new_alert)
        db.session.commit()
        return redirect('/index.html')
    else:
        app.logger.debug('Landing Page Visited without method POST')
        all_alerts = Alert.query.order_by(Alert.date_added).all()
        all_users = User.query.order_by(User.id).all()
        return render_template('index.html', alerts=all_alerts, users=all_users)

def get_bool(string):
    if string == "True" or string == "true":
        return True
    return False

@app.route('/alerts', methods=['GET', 'POST'])
def alerts():
    app.logger.info('Requesting Alerts. (/alerts)')
    if request.method == 'POST':
        app.logger.info('Adding New Alert. (/alerts)')

        # Creating App Alert
        messenger_bool = get_bool(request.form['messenger'])
        telegram_bool = get_bool(request.form['telegram'])
        discord_bool = get_bool(request.form['discord'])
        new_apps_bool = Apps(discord=discord_bool, telegram=telegram_bool, messenger=messenger_bool)

        # First we add the app alert, then flush to retrieve it's unique ID
        db.session.add(new_apps_bool)
        db.session.flush()

        # Creating new Alert
        alert_title = request.form['title']
        alert_page = request.form['page']
        current_user_id = session["_user_id"]
        apps_bools_id = new_apps_bool.id
        #new_alert = Alert(title=alert_title, page=alert_page, user_id=current_user_id, apps_id=apps_bools_id)
        new_alert = Alert(title=alert_title, page=alert_page)
        db.session.add(new_alert)
        db.session.commit()

        all_alerts = Alert.query.order_by(Alert.date_added).all()
        return render_template('index.html', alerts=all_alerts, emailuser=session['email'])
    else:
        if session["remember_me"]:
            app.logger.info('User was logged in - printing his site.')
            all_alerts = Alert.query.order_by(Alert.date_added).all()
            return render_template('index.html', alerts=all_alerts, emailuser=session['email'])
        else:
            app.logger.info('User was not logged in - printing landing page.')
            print(session)
            return render_template('index.html')

@app.route('/alerts/delete/<int:id>')
def delete(id):
    app.logger.info(f'Deleting Alert with ID: {id}')
    alert = Alert.query.get_or_404(id)
    db.session.delete(alert)
    db.session.commit()
    return redirect('/index.html')

# Edits are now SO SMOOTH - edited by editing it directly on the index site
@app.route('/alerts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    app.logger.info(f'Trying to edit Alert with ID: {id}')
    alert = Alert.query.get_or_404(id)
    if request.method == 'POST':
        alert.title = request.form['title']
        alert.page = request.form['page']
        db.session.commit()
        app.logger.info(f'Edited Alert with ID: {id}')

    return redirect('/index.html')

@app.route('/alerts/new', methods=['GET', 'POST'])
def new_alert():
    app.logger.info('Adding New Alert (/alerts/new).')
    if request.method == 'POST':
        alert.title = request.form['title']
        alert.page = request.form['page']
        new_alert = Alert(title=alert_title, page=alert_page)
        db.session.add(new_alert)
        db.session.commit()
        return redirect('/index.html')


@app.route('/index.html', methods=['GET', 'POST'])
def go_home():
    all_alerts = Alert.query.order_by(Alert.date_added).all()
    return render_template('index.html', alerts=all_alerts, emailuser=session['email'])

if __name__ == "__main__":
    app.run(debug=True)