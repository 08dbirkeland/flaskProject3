import os

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Identity

app = Flask(__name__)

base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, "accounts.db")
db = SQLAlchemy(app)


class Accounts(db.Model):
    id = db.Column(db.Integer, Identity(), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __init__(self, name, password, id=None):
        self.name = name
        self.password = password


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        if db.session.query(Accounts).filter(Accounts.name == request.form['username']).count() != 0:
            error = "That user already exists!"
        else:
            db.session.merge(Accounts(request.form['username'], request.form['password']))
            db.session.commit()
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

    return render_template('login.html', error=error)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/passwords')
def passwords():
    return str([it.password for it in db.session.query(Accounts).all()])


# if __name__ == '__main__':
with app.app_context():
    db.create_all()
