from tabs import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    tabs = db.relationship('Tab', backref='owner', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Tab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tab_name = db.Column(db.String(240), nullable=False)
    url = db.Column(db.String(240), nullable=False)
    comment = db.Column(db.UnicodeText())
    use_comment_as_name = db.Column(db.Boolean, default=False)
    clicks = db.Column(db.Integer, nullable=False, default=0)
    favicon = db.Column(db.String(240), default='favicon.ico')
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Tab('{self.tab_name}', '{self.url}', '{self.comment}')"
