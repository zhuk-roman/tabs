from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from os import path
from socket import gethostname

app = Flask(__name__)
bcrypt = Bcrypt(app)
hostname = gethostname()
app.config['SECRET_KEY'] = 'd9a4c31dc056daeb3c17ccff4c879eb0058145fab9fd881543409b019a3647b7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://tabs:76EYtYCq@tabs.cl0rwnday2rr.eu-central-1.rds.amazonaws.com/tabs'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
app.config['USE_SESSION_FOR_NEXT'] = True


from tabs import routes
db.create_all()