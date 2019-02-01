from flask import render_template, flash, redirect, url_for, request
import os
from app import app, db
from app.forms import RegistrationForm, LoginForm, NewTripForm, NewPasswordForm, EditForm, TripPageForm, JoinATripForm, HomeSearchForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Trip, Comments, JoinTrip
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

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

@app.route('/home/', methods=['GET', 'POST'])
@login_required
def home():
    trip = Trip.query.first()
    form = HomeSearchForm()
    if form.validate_on_submit():
        home_search()
    if trip is not None:
        all_trips = Trip.query.all()
        data = []
        for trips in all_trips:
            trips_data = {'location' : trips.location, 'about' : trips.about, 'rating' : trips.trip_rating, 'cost' : trips.total_cost, 'id' : trips.id, 'picture' : trips.trip_picture}
            data.append(trips_data)
        return render_template('home.html', title='Home', data= data, form= form)
    return render_template('home.html', title='Home')

def home_search():
    trips = Trip.query.all()
    form = HomeSearchForm()
    trips = Trip.query.filter_by(location = form.search.data)
    data = []
    for trip in trips:
        trips_data = {'location' : trip.location, 'about' : trip.about, 'rating' : trip.trip_rating, 'cost' : trip.total_cost, 'id' : trip.id, 'picture' : trip.trip_picture}
        data.append(trips_data)
    return render_template('home.html', title='Home', data= data, form= form)

@app.route('/home/my_trips')
@login_required
def my_trips():
    trip = Trip.query.first()
    if trip is not None:
        all_trips = Trip.query.filter_by(creator_id=current_user.id)
        data = []
        for trips in all_trips:
            trips_data = {'location' : trips.location, 'about' : trips.about, 'rating' : trips.trip_rating, 'cost' : str(trips.total_cost) + ' kn', 'id' : trips.id}
            data.append(trips_data)
        return render_template('home.html', title='Home', data= data)
    return render_template('home.html', title='Home')

@app.route('/home/trips_i_joined')
@login_required
def trips_i_joined():
    trip = Trip.query.first()
    if trip is not None:
        data = []
        form_join = JoinTrip.query.filter_by(user_id = current_user.id)
        for items in form_join:
            form_join_trip = Trip.query.filter_by(id = items.trip_id)
            for trips in form_join_trip:
                trips_data = {'location' : trips.location, 'about' : trips.about, 'rating' : trips.trip_rating,
                'cost' : str(trips.total_cost) + ' kn', 'id' : trips.id}
                data.append(trips_data)
        return render_template('home.html', title='Home', data= data)
    return render_template('home.html', title='Home')

@app.route('/trip/<trip_id>', methods=['GET', 'POST'])
@login_required
def trip(trip_id):
    trip = Trip.query.filter_by(id = trip_id).first()
    user = User.query.filter_by(id = trip.creator_id).first()
    comments = Comments.query.filter_by(trip_id = trip.id)
    joined_user = JoinTrip.query.filter_by(trip_id = trip.id)
    c_data = []
    people_going = []
    me_going = False
    if comments is not None:
        for comment in comments:
            user2 = User.query.filter_by(id = comment.user_id).first()
            comment_data = {'comment' : comment.coments, 'username' : user2.username, 'user_picture' : user2.user_picture}
            c_data.append(comment_data)
    if joined_user is not None:
        for people in joined_user:
            user3 = User.query.filter_by(id= people.user_id).first()
            if user3 == current_user:
                me_going = True
            people_data = {'username' : user3.username}
            people_going.append(people_data)
    trip_data = {'trip' : trip.id, 'location' : trip.location, 'about' : trip.about, 'rating' : trip.trip_rating, 'cost' : str(trip.total_cost) + ' kn',
    'date' : trip.date.strftime('%d/%m/%Y'), 'transport' : trip.transport, 'creator' : user.username, 'comments' : c_data, 'users' : people_going,
    'picture' : trip.trip_picture, 'me_going' : me_going}
    form_comments = TripPageForm()
    form_join = JoinATripForm()
    if form_comments.validate_on_submit():
        comment = Comments(coments = form_comments.comment.data, user_id = current_user.id, trip_id = trip.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('trip', trip_id=trip.id))
    elif form_join.validate_on_submit() and me_going == False:
        user_joins = JoinTrip(trip_id = trip.id, user_id = current_user.id)
        db.session.add(user_joins)
        db.session.commit()
        return redirect(url_for('trip', trip_id=trip.id))
    elif form_join.validate_on_submit() and me_going == True:
        user_joins = JoinTrip.query.filter_by(trip_id = trip.id, user_id = current_user.id).first()
        db.session.delete(user_joins)
        db.session.commit()
        return redirect(url_for('trip', trip_id=trip.id))
    return render_template('trip.html', title='Trip', data = trip_data, lform=form_comments, rform = form_join)


@app.route('/newtrip', methods=['GET', 'POST'])
@login_required
def newtrip():
    form = NewTripForm()
    if form.validate_on_submit():
        if form.picture.data is not None:
            filename = secure_filename(form.picture.data.filename)
            form.picture.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        newtrip = Trip(location = form.location.data,
            transport= form.transport.data,
            min_people= int(form.min_people.data),
            max_people= int(form.max_people.data),
            about= form.about.data,
            date = form.date.data,
            total_cost = int(form.total_cost.data),
            creator_id = current_user.id,
            trip_picture = filename)
        db.session.add(newtrip)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('newTrip.html', title='New Trip', form=form)

@app.route('/newpassword', methods=['GET', 'POST'])
def newpassword():
    form = NewPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid username')
            return redirect(url_for('newpassword'))
        user.set_password(form.password_new.data)
        db.session.add(user)
        db.session.commit()
        flash('You changed your password!')
        return redirect(url_for('login'))
    return render_template('newPassword.html', title='New Password', form = form)

@app.route('/edit', methods= ['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.oldpassword.data):
            flash('Your old password isn\'t correct')
        else:
            current_user.set_password(form.password.data)

        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.bio = form.bio.data
        current_user.spol = form.spol.data
        if form.picture.data is not None:
            filename = secure_filename(form.picture.data.filename)
            form.picture.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_user.user_picture = filename
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', title='Edit Profile', form = form)

@app.route('/profile/<id>', methods = ['GET', 'POST'])
@login_required
def profile(id):
    edit_btn = False
    user = User.query.filter_by(username = id).first()
    if user == current_user:
        edit_btn = True
    past_trips = JoinTrip.query.filter_by(user_id = user.id)
    past_trips_data = []
    if past_trips is not None:
        for items in past_trips:
            trip = Trip.query.filter_by(id = items.trip_id).first()
            trip_data = {'location' : trip.location, 'id' : trip.id}
            past_trips_data.append(trip_data)
    user_data = {'username' : user.username, 'first_name' : user.first_name, 'last_name' : user.last_name, 
    'sex' : user.spol, 'bio' : user.bio, 'email' : user.email, 'picture' : user.user_picture, 'past_trips' : past_trips_data,
    'remove_edit' : edit_btn}
    return render_template('profile.html', title="Profile", data = user_data)
