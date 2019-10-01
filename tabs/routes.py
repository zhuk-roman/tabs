from flask import render_template, url_for, flash, redirect, request, abort
from sqlalchemy.engine import url
from tabs.forms import RegistrationForm, LoginForm, UpdateAccountForm, TabForm
from tabs.models import User, Tab
from tabs import app, db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required
import requests
from bs4 import BeautifulSoup


# Set headers
headers = requests.utils.default_headers()
headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            print(request.args)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    flash('Logged Out.', 'success')
    return redirect(url_for('home'))

@app.route("/account/",  methods=['GET', 'POST'])
# @fresh_login_required
@login_required
def account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
        if form.new_password.data:
            current_user.email = form.email.data
            current_user.username = form.username.data
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            db.session.commit()
            flash(f'Account has been updated!', 'success')
        else:
            current_user.email = form.email.data
            current_user.username = form.username.data
            db.session.commit()
            flash(f'Account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', form=form)

@app.route('/tabs/')
@login_required
def tabs():
    tab_set = current_user.tabs
    return render_template('tabs.html', tabs=tab_set)

@app.route("/tabs/add/",  methods=['GET', 'POST'])
@login_required
def add_tab():
    form = TabForm()
    if form.validate_on_submit():
        if (not form.tab_name.data):
            url = form.url.data
            req = requests.get(url, headers)
            soup = BeautifulSoup(req.content)
            form.tab_name.data = soup.title.string
        tab = Tab(tab_name=form.tab_name.data, url=form.url.data, user_id=current_user.id,
                  use_comment_as_name=form.use_comment_as_name.data, comment=form.comment.data)
        db.session.add(tab)
        db.session.commit()
        flash('Tab created!', 'success')
        return redirect(url_for('tabs'))
    return render_template('add_tab.html', legend='Create Tab', form=form)

@app.route("/tabs/<int:tab_id>/edit/",  methods=['GET', 'POST'])
@login_required
def edit_tab(tab_id):
    tab = Tab.query.get_or_404(tab_id)
    if tab.user_id != current_user.id:
        abort(403)
    form = TabForm()
    if form.validate_on_submit():
        if (not form.tab_name.data):
            url = form.url.data
            req = requests.get(url, headers)
            soup = BeautifulSoup(req.content)
            form.tab_name.data = soup.title.string
        tab.tab_name = form.tab_name.data
        tab.url = form.url.data
        tab.comment = form.comment.data
        tab.use_comment_as_name = form.use_comment_as_name.data
        db.session.add(tab)
        db.session.commit()
        flash('Updated.', 'success')
        return redirect(url_for('tabs', tab_id=tab.id))
    elif request.method == 'GET':
        form.tab_name.data = tab.tab_name
        form.url.data = tab.url
        form.comment.data = tab.comment
        form.use_comment_as_name.data = tab.use_comment_as_name
    return render_template('add_tab.html', legend='Update Tab', tab=tab, form=form)

@app.route("/tabs/<int:tab_id>/delete/",  methods=['POST'])
@login_required
def delete_tab(tab_id):
    tab = Tab.query.get_or_404(tab_id)
    if tab.user_id != current_user.id:
        abort(403)
    db.session.delete(tab)
    db.session.commit()
    flash('Tab has been deleted!', 'success')
    return redirect(url_for('tabs'))