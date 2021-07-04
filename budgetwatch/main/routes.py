from flask import render_template, url_for, Blueprint, flash, redirect
from flask_login import current_user, login_required
from budgetwatch.entry.forms import DataEntryForm
from budgetwatch.models import Entry
from budgetwatch import db

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = DataEntryForm()
    if form.validate_on_submit():
        entry = Entry(item=form.item.data.capitalize(), category=form.category.data.capitalize(), price=str(form.price.data), location=form.location.data.capitalize(), date_posted=form.date.data, user_id=current_user.id)
        db.session.add(entry)
        db.session.commit()
        flash('Data has been entered', 'success')
        return redirect(url_for('main.home'))
    return render_template('home.html', form=form)
