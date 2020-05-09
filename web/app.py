from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'xDDDDsupresikretKEy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notifayy.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# User_ID = Primary Key
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# TODO: Alert has User ID to determine whose Alert it is
# TODO: Booleans for various supported messaging apps
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    page = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'Alert # ' + str(self.id)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __repr__(self):
        return 'User: ' + str(self.email)

@app.route('/register', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']

        # If this returns then it means that this user exists
        user = User.query.filter_by(email=user_email).first() 

        # If user doesn't exist, redirect back
        if user: 
            flash('Email address already exists')
            return redirect('/index.html')

        # TODO: Hash the Password
        new_user = User(email=user_email, password=user_password)

        # Add new user to DB
        db.session.add(new_user)
        db.session.commit()

        return redirect('/index.html')
    else:
        all_alerts = Alert.query.order_by(Alert.date_added).all()
        all_users = User.query.order_by(User.id).all()
        return render_template('index.html', alerts=all_alerts, users=all_users)

@app.route('/login', methods=['POST'])
def login_post():
    if request.method == 'POST':
        user_email = request.form.get('email')
        user_password = request.form.get('password')

        # TODO: Remember me checkbox in login form
        # remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=user_email).first()

        # TODO: Hash password and check it with has in db
        if not user or not (user.password == user_password):
            flash('Please check your login details and try again.')
            return redirect('/index.html') 

        login_user(user, remember=True)
        all_alerts = Alert.query.order_by(Alert.date_added).all()
        return render_template('index.html', alerts=all_alerts, emailuser=user_email)

    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        alert_title = request.form['title']
        alert_page = request.form['page']
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
    if request.method == 'POST':
        alert_title = request.form['title']
        alert_page = request.form['page']
        new_alert = Alert(title=alert_title, page=alert_page)
        db.session.add(new_alert)
        db.session.commit()
        all_alerts = Alert.query.order_by(Alert.date_added).all()
        return render_template('index.html', alerts=all_alerts, emailuser=alert_user)
    else:
        all_alerts = Alert.query.order_by(Alert.date_added).all()
        return render_template('index.html', alerts=all_alerts)

@app.route('/alerts/delete/<int:id>')
def delete(id):
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
    alert = Alert.query.get_or_404(id)

    if request.method == 'POST':
        alert.title = request.form['title']
        alert.author = request.form['author']
        alert.content = request.form['content']
        db.session.commit()
        return redirect('/index.html')
    else:
        return render_template('edit.html', alert=alert)

@app.route('/alerts/new', methods=['GET', 'POST'])
def new_alert():
    if request.method == 'POST':
        alert.title = request.form['title']
        alert.page = request.form['page']
        new_alert = Alert(title=alert_title, page=alert_page)
        db.session.add(new_alert)
        db.session.commit()
        return redirect('/index.html')


if __name__ == "__main__":
    app.run(debug=True)
