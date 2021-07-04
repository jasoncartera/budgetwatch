from datetime import date, datetime
from flask import render_template, url_for, flash, redirect, request, abort
from budgetwatch import app, db, bcrypt, mail
from budgetwatch.forms import RegistrationForm, LoginForm, DataEntryForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from budgetwatch.models import User, Entry
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import extract
from datetime import datetime
import calendar
from pytz import timezone
from flask_mail import Message

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = DataEntryForm()
    if form.validate_on_submit():
        entry = Entry(item=form.item.data.capitalize(), category=form.category.data.capitalize(), price=str(form.price.data), location=form.location.data.capitalize(), date_posted=form.data.data, user_id=current_user.id)
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
    month = datetime.today().month
    year = datetime.today().year
    entries = Entry.query.filter_by(user_id=current_user.id).filter(extract('month', Entry.date_posted)==month).filter(extract('year', Entry.date_posted)==year).all()
    category_sum = db.session.query(Entry.category, db.func.sum(Entry.price)).group_by(Entry.category).filter(extract('month', Entry.date_posted)==month).filter(extract('year', Entry.date_posted)==year).all()
    return render_template('summary.html', title='Account Summary', entries=entries, category_sum=category_sum, month=calendar.month_name[month], year=year)


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

@app.route('/update/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def update_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if entry.user != current_user:
        abort(403)
    form = DataEntryForm()
    if form.validate_on_submit():
        entry.item = form.item.data
        entry.category = form.category.data
        entry.price = str(form.price.data)
        entry.location = form.location.data
        entry.date_posted = form.date.data
        db.session.commit()
        flash('Your entry has been updated', 'success')
        return redirect(url_for('summary'))
    elif request.method == 'GET':
        form.item.data = entry.item
        form.category.data = entry.category
        form.price.data = float(entry.price)
        form.location.data = entry.location
        form.date.data = entry.date_posted
    return render_template('update.html', title='Update Entry', form=form, entry=entry)

@app.route('/update/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if entry.user != current_user:
        abort(403)
    db.session.delete(entry)
    db.session.commit()
    flash('Your entry has been deleted', 'success')
    return redirect(url_for('summary'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@budgetwatch.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then ignore this email.
'''
    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Password has been updated, you can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)