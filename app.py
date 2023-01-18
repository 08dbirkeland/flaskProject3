import os
import yfinance as yf
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Identity

app = Flask(__name__)

base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, "accounts.db")
db = SQLAlchemy(app)


# This code creates a database at the given directory


class Accounts(db.Model):
    id = db.Column(db.Integer, Identity(), primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    # This establishes a database with a primarykey id and a username and password field

    def __init__(self, name, password, id=None):
        self.name = name
        self.password = password


class RegisterError(Exception):
    pass


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        if db.session.query(Accounts).filter(Accounts.name == request.form['username']).count() != 0:
            error = "That user already exists!"
        # Checks if there is any accounts with the username currently stored in the database
        else:
            try:
                if len(request.form['username']) <= 3 or len(request.form['username']) >= 30:
                    raise RegisterError("Username is not a valid length")
                if len(request.form['password']) <= 3 or len(request.form['password']) >= 40:
                    raise RegisterError("Password is not a valid length")
                # Check if the username or password aren't too short
                if not (request.form['username'].isalnum()):
                    raise RegisterError("Username must only contains English characters")
                if not (request.form['password'].isalnum()):
                    raise RegisterError("Password must only contains English characters")
                # Checks if the username and password only contains alphanumeric characters
                db.session.merge(Accounts(request.form['username'], request.form['password']))
                db.session.commit()
                # Adds an account with the given username and password then commits it to the database
            except RegisterError as e:
                print(e)
            else:
                return redirect(url_for('home'))
    return render_template('register.html', error=error)


class LoginError(Exception):
    pass


def _try_login(username, password):
    user = db.session.query(Accounts).filter(Accounts.name == username).one_or_none()
    if user is None:
        raise LoginError("That user does not exist!")
    if user.password != password:
        raise LoginError("Incorrect password!")
    return user


# Attempts to log in, however, if password or the username are incorrect an error will appear


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            _try_login(request.form["username"], request.form["password"])
        except LoginError as e:
            error = e.args[0]
        else:
            return redirect(url_for('home'))
    # Attempts to log in if an exception occurs output the error
    return render_template('login.html', error=error)


@app.route('/')
def home():
    data = yf.download(tickers='BTC-GBP', period='24h', interval='1h')
    data_dict = {outer_key: {str(k): v for k, v in outer_value.items()} for outer_key, outer_value in
                 data.to_dict().items()}
    return render_template('home.html', data=data_dict)


@app.route('/passwords')
def passwords():
    return str([it.password for it in db.session.query(Accounts).all()])


# if __name__ == '__main__':
with app.app_context():
    db.create_all()
