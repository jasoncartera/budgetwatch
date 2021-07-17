from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from budgetwatch import db
from budgetwatch.entry.forms import DataEntryForm
from budgetwatch.models import Entry
from flask_login import current_user, login_required
from sqlalchemy import extract
from datetime import datetime
import calendar

entry = Blueprint('entry', __name__)

@entry.route('/summary')
@login_required
def summary():
    month = datetime.today().month
    year = datetime.today().year
    entries = Entry.query.filter_by(user_id=current_user.id).filter(extract('month', Entry.date_posted)==month).filter(extract('year', Entry.date_posted)==year).all()
    category_sum = db.session.query(Entry.category, db.func.sum(Entry.price)).group_by(Entry.category).filter(extract('month', Entry.date_posted)==month).filter(extract('year', Entry.date_posted)==year).filter(Entry.user_id==current_user.id).all()
    return render_template('summary.html', title='Account Summary', entries=entries, category_sum=category_sum, month=calendar.month_name[month], year=year)


@entry.route('/update/<int:entry_id>', methods=['GET', 'POST'])
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
        entry.date_posted = form.date.data
        db.session.commit()
        flash('Your entry has been updated', 'success')
        return redirect(url_for('entry.summary'))
    elif request.method == 'GET':
        form.item.data = entry.item
        form.category.data = entry.category
        form.price.data = entry.price
        form.location.data = entry.location
        form.date.data = entry.date_posted
    return render_template('update.html', title='Update Entry', form=form, entry=entry)

@entry.route('/update/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if entry.user != current_user:
        abort(403)
    db.session.delete(entry)
    db.session.commit()
    flash('Your entry has been deleted', 'success')
    return redirect(url_for('entry.summary'))