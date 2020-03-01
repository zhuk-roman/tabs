from flask import render_template, url_for, flash, redirect, request, abort
from sqlalchemy.engine import url
from tabs.forms import RegistrationForm, LoginForm, UpdateAccountForm, TabForm
from tabs.models import User, Tab
from tabs import app, db, bcrypt, hostname
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required
import requests
import favicon
import random
from datetime import date
from bs4 import BeautifulSoup

# Set headers
headers = requests.utils.default_headers()
headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})


# @app.route('/')
# def home():
#     return render_template('home.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('tabs'))
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
        return redirect(url_for('tabs'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            print(request.args)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('tabs'))
        else:
            flash('Login Unsuccessful.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    flash('Logged Out.', 'success')
    return redirect(url_for('tabs'))


@app.route("/account/", methods=['GET', 'POST'])
# @fresh_login_required
@login_required
def account():
    form = UpdateAccountForm()
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


@app.route('/')
@login_required
def tabs():
    tab_set = current_user.tabs
    return render_template('tabs.html', hostname=hostname, tabs=tab_set)

def host_alive(url):
    try:
        requests.get(url, headers)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        flash(f'{url} not responding!', 'danger')
        return False
    except requests.exceptions.HTTPError:
        return True
    else:
        return True

@app.route("/tabs/add/", methods=['GET', 'POST'])
@login_required
def add_tab():
    form = TabForm()
    if form.validate_on_submit():
        url = form.url.data
        if not host_alive(url):
            return render_template('add_tab.html', legend='Create Tab', form=form)
        if (not form.tab_name.data):
            # url = form.url.data
            req = requests.get(url, headers)
            soup = BeautifulSoup(req.content)
            if soup.title:                                       # if title exist
                form.tab_name.data = soup.title.string
            if not form.tab_name.data:                           # if tab_name is missing print url instead
                form.tab_name.data = url

        try:
            favicon_obj = favicon.get(url)
        except requests.exceptions.HTTPError as e:
            favicon_obj = None
            print('favicon.get(url) error = ' + str(e.response.status_code))
        if favicon_obj:                                          #save favicon if there is one
            favicon_url = favicon.get(url)[0].url
            r = requests.get(favicon_url, allow_redirects=True)
            favicon_file_name = str(random.randint(0,10**9)) + date.today().strftime('_%d_%m_%Y') + '.ico'
            try:
                open(app.static_folder + '/img/' + favicon_file_name, 'wb').write(r.content)
            except (FileNotFoundError):
                print('FileNotFoundError' + app.static_folder + '/img/' + favicon_file_name)
        else:
            favicon_file_name = None
        tab = Tab(tab_name=form.tab_name.data, url=form.url.data, user_id=current_user.id,
                  use_comment_as_name=form.use_comment_as_name.data, comment=form.comment.data,
                  favicon=favicon_file_name)
        db.session.add(tab)
        db.session.commit()
        flash('Tab created!', 'success')
        return redirect(url_for('tabs'))
    return render_template('add_tab.html', legend='Create Tab', form=form)


@app.route("/tabs/<int:tab_id>/edit/", methods=['GET', 'POST'])
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


@app.route("/tabs/<int:tab_id>/delete/", methods=['POST'])
@login_required
def delete_tab(tab_id):
    tab = Tab.query.get_or_404(tab_id)
    if tab.user_id != current_user.id:
        abort(403)
    db.session.delete(tab)
    db.session.commit()
    flash('Tab has been deleted!', 'success')
    return redirect(url_for('tabs'))

