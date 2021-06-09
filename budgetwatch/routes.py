from flask import render_template, url_for, flash, redirect, request, abort
from budgetwatch import app, db, bcrypt
from budgetwatch.forms import RegistrationForm, LoginForm, DataEntryForm, UpdateAccountForm
from budgetwatch.models import User, Entry
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = DataEntryForm()
    if form.validate_on_submit():
        entry = Entry(item=form.item.data, category=form.category.data, price=str(form.price.data), location=form.location.data, date_posted=form.date.data, user_id=current_user.id)
        db.session.add(entry)
        db.session.commit()
        flash('Data has been entered', 'success')
        return redirect(url_for('home'))
    return render_template('home.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}, you can now login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/summary')
@login_required
def summary():
    entries = Entry.query.filter_by(user_id=current_user.id).limit(5)
    return render_template('summary.html', title='Account Summary', entries=entries)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('settings'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('settings.html', title='Account Settings', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/home/<int:entry_id>/update', methods=['GET', 'POST'])
@login_required
def update_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if entry.user != current_user:
        abort(403)
    form = DataEntryForm()
    if form.validate_on_submit():
        entry.item = form.item.data
        entry.category = form.category.data
        entry.price = form.price.data
        entry.location = form.location.data
        db.session.commit()
        flash('Your entry has been updated', 'success')
        return redirect(url_for('summary'))
    elif request.method == 'GET':
        form.item.data = entry.item
        form.category.data = entry.category
        form.price.data = float(entry.price)
        form.location.data = entry.location
    return render_template('home.html', title='Update Entry', form=form)