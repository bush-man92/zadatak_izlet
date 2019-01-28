from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import RegistrationForm, LoginForm, NewTripForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse

@app.route('/register', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
       	return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
	return render_template('home.html', title='Home')

@app.route('/trip')
@login_required
def trip():
	return render_template('trip.html', title='Trip')

@app.route('/newtrip', methods=['GET', 'POST'])
@login_required
def newtrip():
    form = NewTripForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            l = Trip(location = 'vz')
            db.session.add(l)
            db.session.commit()

            newtrip = Trip(request.form['location'], request.form['transport'], request.form['min_people'], request.form['max_people'], request.form['about'], request.form['data'], request.form['total_cost'])
            db.session.add(newtrip)
            db.session.commit()
            return redirect(url_for('newTrip.html'))
    return render_template('newTrip.html', title='New Trip', form=form)

