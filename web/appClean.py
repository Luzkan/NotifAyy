import logging
from flask import Flask, render_template, request, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user
from datetime import datetime
from passlib.hash import sha256_crypt

import msnotifier.bot.siteMonitor as siteMonitor
import threading
import msnotifier.messenger as messenger

import DataBaseStructure as dbs



# -------------------------------------------------------
# -- Sending class is a Thread that sends all given changes with all communication channels
# --
# -- __init__ has param @changes which is a List of Tuples (int,str) where int is alert_id and str
# -- is a content of a change assigned for that alert_id
# -- Thanks to given alert_id, we take out of the db inforamtion about user we have to send changes
# -- If communication channel is a Discord, Thread add given change to Db Table changes. Other channels
# -- are being handeled thanks to messenger.py module that is abstract class handling logging into email/fb/telegram(undone)
# -- and sending message
# -- closes after job's done

class Sending(threading.Thread):
    def __init__(self,changes):
        threading.Thread.__init__(self)
        self.changes =changes
    def run(self):
        for item in  self.changes:
            content=item[1]
            alert_id=item[0]
            al, user, apps = dbs.get_everything(alert_id)
            alertwebpage=al.page
            mail=apps.email
            msng=apps.messenger
            discord=apps.discord
            if mail==True:
                email=user.email
                notifier= messenger.mail_chat()
                notifier.log_into(email,"")
                notifier.message_myself(content,alertwebpage)
            if msng==True:
                fblogin=user.messenger_l
                fbpass=user.messenger_token
                notifier= messenger.mail_chat()
                notifier.log_into(fblogin,fbpass)
                notifier.message_myself(content,alertwebpage)
            if discord==True:
                dbs.add_to_changes(item)

# -- Thread that works always, it detects changes with siteMonitor module and starting SENDING Thread if there is any changes to send
# -- IN: List of Alerts Alert- Tuple(alert_id,alert_webpage)
# -- OUT: changes List of Tuple(alert_id, change)
class Detecting(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.alerts=[]

    def get_all_alerts(self):
        return [(i.id, i.page) for i in dbs.allAlerts()]
    def delete_alert(self,alert_id):
        for alert in self.alerts:
            if alert[0]==alert_id:
                self.alerts.remove(alert)
                return 1
        return -1

    def add_alert(self,alert_id,adr):
        self.alerts.append((alert_id,adr))
    def run(self):
        self.alerts = self.get_all_alerts()
        while(True):

            tags = ["h1", "h2", "h3", "p"]
            changes=siteMonitor.get_diffs_string_format(siteMonitor.get_diffs(tags,[alert[0] for alert in self.alerts],[alert[1] for alert in self.alerts],16),tags)


            if len(changes)!=0:
                Sending(changes).start()


o=Detecting()
o.start()
# ---------------------------------------
#  -  Helping Functions for Site Walk  -

def remember_me_handle():
    if "_user_id" in session:
        if session["remember_me"]:
            dbs.app.logger.info('User was logged in - printing his site.')
            all_alerts = dbs.get_alerts()
            return render_template('index.html', alerts=all_alerts, emailuser=session['email'])
        else:
            dbs.app.logger.info('User was not logged in - printing landing page.')
            return redirect('/index.html')
    else:
        return render_template('index.html')

def get_bool(string):
    if string == "True" or string == "true":
        return True
    return False

# -----------------------
#  - Main HREF Routes  -

@dbs.app.route('/register', methods=['GET', 'POST'])
def auth():
    dbs.app.logger.info('Registration Button pressed.')
    if request.method == 'POST':

        dbs.app.logger.info('Method: POST')
        user_email = request.form['email']
        user_password = request.form['password']

        # If this returns then it means that this user exists
        user = dbs.User.query.filter_by(email=user_email).first() 

        # If user doesn't exist, redirect back
        if user: 
            flash('Email address already exists')
            dbs.app.logger.warning("Email adress already exist in the database.")
            return redirect('/')
        dbs.app.logger.info("Succesfully added new user to database.")

        # Hashing the Password
        password_hashed = sha256_crypt.hash(user_password)
        new_user = dbs.User(email=user_email, password=password_hashed)

        # Add new user to DB
        dbs.db.session.add(new_user)
        dbs.db.session.commit()

        flash('Registration went all fine! :3 You can now log in!')
        return redirect('/')
    else:
        dbs.app.logger.warning("User somehow didn't use Method: POST.")
        flash('Something went wrong with sending the registration informations.')
        return redirect('/')

@dbs.app.route('/login', methods=['POST'])
def login_post():
    dbs.app.logger.info('Login Button Pressed.')
    if request.method == 'POST':

        # Get User Informations from Form
        user_email = request.form.get('email')
        user_password = request.form.get('password')
        remember = request.form.get('remember')
        user = dbs.User.query.filter_by(email=user_email).first()

        # Checking if this user exist (doing this and pass check will throw err, if user is not in db, hence no pass)
        if not user:
            flash("There's no registered account with given email adress.")
            dbs.app.logger.warning(" User doesn't exist: " + user_email)
            return redirect('/') 

        # --- Password Check
        #     Info: I'm printing hashed version, but we actually compare the original string with hashed version in db
        pass_check = (sha256_crypt.verify(user_password, user.password))
        dbs.app.logger.info(f"Result of pass check: {pass_check} - (input: {sha256_crypt.hash(user_password)}, db: {user.password})")
        # ---

        # Verifying Password
        if not user or not pass_check:
            flash('Please check your login details and try again.')
            dbs.app.logger.warning("Wrong Credentials" + user_email)
            return redirect('/') 
        dbs.app.logger.info("Succesfully logged in user: " + user_email)
        
        # Remember Me Handling (saving in session and in param)
        login_user(user, remember=remember)
        session["remember_me"] = True if remember else False
        session["email"] = user_email
        
        # Apps Quality of Life display if already defined by user
        session["disc"] = user.discord_id
        session["mess"] = user.messenger_l
        session["tele"] = user.telegram_id
        if user.discord_id == None:
            session["disc"] = ""
        if user.messenger_l == None:
            session["mess"] = ""
        if user.telegram_id == None:
            session["tele"] = ""
    
        # Getting Alerts and loading the page for this user
        return redirect('/index.html')
    else:
        return remember_me_handle()

    return redirect('/')

@dbs.app.route('/alerts', methods=['GET', 'POST'])
def alerts():
    if request.method == 'POST':
        dbs.app.logger.info('Adding New Alert.')

        # Creating App Alert
        messenger_bool = get_bool(request.form['messenger'])
        telegram_bool = get_bool(request.form['telegram'])
        discord_bool = get_bool(request.form['discord'])
        email_bool = get_bool(request.form['email'])
        new_apps_bool = dbs.Apps(discord=discord_bool, telegram=telegram_bool, messenger=messenger_bool, email=email_bool)

        # First we add the app alert, then flush to retrieve it's unique ID
        dbs.db.session.add(new_apps_bool)
        dbs.db.session.flush()

        # Creating new Alert
        alert_title = request.form['title']
        alert_page = request.form['page']
        current_user_id = session["_user_id"]
        apps_bools_id = new_apps_bool.id
        new_alert = dbs.Alert(title=alert_title, page=alert_page, user_id=current_user_id, apps_id=apps_bools_id)
        dbs.db.session.add(new_alert)
        dbs.db.session.flush()
        o.add_alert(new_alert.id,new_alert.page)
        dbs.db.session.commit()

        return redirect('/index.html')
    else:
        dbs.app.logger.info('Loading Landing Page or User Main Page.')
        return remember_me_handle()

# --------------------------------
#  - Editing / Deleting Alerts  -

@dbs.app.route('/alerts/delete/<int:id>')
def delete(id):
    dbs.app.logger.info(f'Deleting Alert with ID: {id}')
    alert = dbs.Alert.query.get_or_404(id)
    dbs.db.session.delete(alert)
    o.delete_alert(alert.id)
    dbs.db.session.commit()
    return redirect('/index.html')

# Made the alert editing very smooth - everything is handled from mainpage
@dbs.app.route('/alerts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    dbs.app.logger.info(f'Trying to edit Alert with ID: {id}')

    # Retrieving the edited Alert from DB
    o.delete_alert(id)
    alert = dbs.Alert.query.get_or_404(id)
    apps = dbs.Apps.query.get_or_404(alert.apps_id)
    if request.method == 'POST':
        dbs.app.logger.info(f'Editing Alert with ID: {id}')

        # Receiving new inputs for this alert
        alert.title = request.form['title']
        alert.page = request.form['page']
        apps.messenger = get_bool(request.form['messenger'])
        apps.telegram = get_bool(request.form['telegram'])
        apps.discord = get_bool(request.form['discord'])
        apps.email = get_bool(request.form['email'])

        # Updating the alert in DB
        o.add_alert(alert.id, alert.page)
        dbs.db.session.commit()
        dbs.app.logger.info(f'Edited Alert with ID: {id}')

    return redirect('/index.html')

# -----------------------------------------
#  - Linking Discord/Messenger/Telegram  -

@dbs.app.route('/discord_link', methods=['POST'])
def discord_link():
    dbs.app.logger.info(f'Trying to link discord id.')

    # Retrieving the current User info from DB
    user = dbs.User.query.get_or_404(session["_user_id"])
    if request.method == 'POST':

        # Receiving new inputs for this alert
        user.discord_id = request.form['discord_id']
        session["disc"] = user.discord_id

        # Updating the alert in DB
        dbs.db.session.commit()
        dbs.app.logger.info(f"Linked Discord for user {session['_user_id']} - id: {user.discord_id}")

    return redirect('/index.html')

@dbs.app.route('/messenger_link', methods=['POST'])
def messenger_link():
    dbs.app.logger.info(f'Trying to link messenger credentials.')
    user = dbs.User.query.get_or_404(session["_user_id"])
    if request.method == 'POST':
        # Deadline Request Feature
        user.messenger_l = request.form['messenger_l']

        # It's bad idea to store plain password String in db
        # messenger_p variable contains fb password
        messenger_p = request.form['messenger_p']

        session["mess"] = user.messenger_l
        dbs.db.session.commit()
        dbs.app.logger.info(f"Linked Messenger for user {session['_user_id']} - login: {user.messenger_l}")
    return redirect('/index.html')

@dbs.app.route('/telegram_link', methods=['POST'])
def telegram_link():
    dbs.app.logger.info(f'Trying to link telegram id.')
    user = dbs.User.query.get_or_404(session["_user_id"])
    if request.method == 'POST':
        user.telegram_id = request.form['telegram_id']
        session["tele"] = user.telegram_id
        dbs.db.session.commit()
        dbs.app.logger.info(f"Linked Telegram for user {session['_user_id']} - id: {user.telegram_id}")
    return redirect('/index.html')

# ------------------------------------
#  - HREF for Mainpage and Logout  -

@dbs.app.route('/')
def index():
    dbs.app.logger.info('Landing Page Visited.')
    return remember_me_handle()

@dbs.app.route('/index.html', methods=['GET', 'POST'])
def go_home():
    all_alerts = dbs.get_alerts()
    return render_template('index.html', alerts=all_alerts, emailuser=session['email'], discsaved=session["disc"], messsaved=session["mess"], telesaved=session["tele"])

@dbs.app.route('/logout', methods=['GET', 'POST'])
def logout():
    dbs.app.logger.info(f"User is logging out: {session['email']}")
    logout_user()
    return redirect('/')

@dbs.app.route('/changes', methods=['GET'])
def changes():
    change = dbs.ChangesForDiscord.query.first()
    if change is None:
        return jsonify({'change': '', 'title': '', 'page': '', 'discid': -1})

    dbs.db.session.delete(change)
    dbs.db.session.commit()
    alrt = dbs.Alert.query.filter_by(id = change.alert_id).first()
    usr = dbs.User.query.filter_by(id = alrt.user_id).first()
    if usr is None:
        return jsonify({'change': '', 'title': '', 'page': '', 'discid': -1})

    result = jsonify({'change': change.content, 'title': alrt.title, 'page': alrt.page, 'discid': usr.discord_id})
    return result



if __name__ == "__main__":
    dbs.app.run(debug=True)
 
 
