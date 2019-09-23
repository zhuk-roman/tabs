#from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd9a4c31dc056daeb3c17ccff4c879eb0058145fab9fd881543409b019a3647b7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    tabs=db.relationship('Tab', backref='owner', lazy=True)
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Tab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(240), nullable=False)
    url = db.Column(db.String(240), nullable=False)
    clicks = db.Column(db.String(240), nullable=False)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"Tab('{self.name}', '{self.url}')"

tabs = [
    {
        'name' : 'tab 1',
        'url' : 'https://google.com'
    },
    {
        'name' : 'tab 2',
        'url' : 'https://google.ru'
    }
]

@app.route('/')
def home(post_id=0):
    # print(dir(app))
    return render_template('about.html', tabs=tabs)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@example.com' and form.password.data == 'password':
            flash('You have been loged in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful.', 'danger')
    return render_template('login.html', title='Login', form=form)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')