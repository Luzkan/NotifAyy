import logging
from flask import Flask, render_template, request, redirect, flash
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
# This is for the FSADeprecationWarning (adds significant overhead)
# and willl be disabled by default in the future anyway
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
            app.logger.warn("Email adress already exist in the database.")
            return redirect('/index.html')

        app.logger.info("Succesfully added new user to database.")
        # Hashing the Password
        password_hashed = sha256_crypt.hash(user_password)
        new_user = User(email=user_email, password=password_hashed)

        # Add new user to DB
        db.session.add(new_user)
        db.session.commit()

        return redirect('/index.html')
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

        # Hash password and check it with the one in db (which was hashed on registration)
        password_hashed = sha256_crypt.hash(user_password)

        # --- Debugging Passwords check
        app.logger.debug("Passwords: (input: " + password_hashed + ", db: " + user.password + ")")
        res = (sha256_crypt.verify(user.password, password_hashed))
        app.logger.debug("Result of pass check: " + str(res))
        # ---

        if not user or not (sha256_crypt.verify(user.password, password_hashed)):
            flash('Please check your login details and try again.')
            app.logger.warn("Wrong Credentials / User doesn't exist" + user_email)
            return redirect('/') 

        app.logger.info("Succesfully logged in user: " + user_email)
        login_user(user, remember=remember)
        all_alerts = Alert.query.order_by(Alert.date_added).all()
        return render_template('index.html', alerts=all_alerts, emailuser=user_email)

    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Creating App Alert
        messenger_bool = request.form['messenger']
        telegram_bool = request.form['telegram']
        discord_bool = request.form['discord']
        new_apps_bool = Apps(discord=discord_bool, telegram=telegram_bool, messenger=messenger_bool)

        # First we add the app alert, then flush to retrieve it's unique ID
        db.session.add(new_apps_bool)
        db.session.flush()

        # Creating new Alert
        alert_title = request.form['title']
        alert_page = request.form['page']
        # TODO: User_ID
        apps_bools_id = new_apps_bool.id
        #new_alert = Alert(title=alert_title, page=alert_page, user_id=current_user_id, apps_id=apps_bools_id)
        new_alert = Alert(title=alert_title, page=alert_page)
        db.session.add(new_alert)
        db.session.commit()
        return redirect('/index.html')
    else:
        all_alerts = Alert.query.order_by(Alert.date_added).all()
        all_users = User.query.order_by(User.id).all()
        return render_template('index.html', alerts=all_alerts, users=all_users)

@app.route('/alerts', methods=['GET', 'POST'])
def alerts():
    alert_user = request.form['currentuser']
    app.logger.info('Requesting Alerts.')
    if request.method == 'POST':
        app.logger.info('Adding New Alert.')
        alert_title = request.form['title']
        alert_page = request.form['page']
        new_alert = Alert(title=alert_title, page=alert_page)
        db.session.add(new_alert)
        db.session.commit()
        all_alerts = Alert.query.order_by(Alert.date_added).all()
        return render_template('index.html', alerts=all_alerts, emailuser=alert_user)
    else:
        app.logger.info('Requesting All Alerts.')
        all_alerts = Alert.query.order_by(Alert.date_added).all()
        return render_template('index.html', alerts=all_alerts)

@app.route('/alerts/delete/<int:id>')
def delete(id):
    app.logger.info('Deleting Alert with ID: ', id)
    alert = Alert.query.get_or_404(id)
    db.session.delete(alert)
    db.session.commit()
    # TODO: Do this properly when a way to pass logged user will be
    #       conceptualized
    # all_alerts = Alert.query.order_by(Alert.date_added).all()
    return redirect('/')

# TODO: Alert Edit to be handled on the same page,
#       by changing <p>'s to <inputs> and edit there
@app.route('/alerts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    app.logger.info('Editing Alert with ID: ', id)
    alert = Alert.query.get_or_404(id)

    if request.method == 'POST':
        app.logger.info('Edited Alert with ID: ', id)
        alert.title = request.form['title']
        alert.author = request.form['author']
        alert.content = request.form['content']
        db.session.commit()
        return redirect('/index.html')
    else:
        app.logger.info('Rendering Site to Edit Alert with ID: ', id)
        return render_template('edit.html', alert=alert)

@app.route('/alerts/new', methods=['GET', 'POST'])
def new_alert():
    app.logger.info('Adding New Alert.')
    if request.method == 'POST':
        alert.title = request.form['title']
        alert.page = request.form['page']
        new_alert = Alert(title=alert_title, page=alert_page)
        db.session.add(new_alert)
        db.session.commit()
        return redirect('/index.html')


if __name__ == "__main__":
    app.run(debug=True)