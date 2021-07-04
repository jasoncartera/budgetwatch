from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, DateTimeField
from wtforms.validators import DataRequired
from datetime import datetime

class DataEntryForm(FlaskForm):
    item = StringField('Item', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    price = DecimalField('Price')
    location = StringField('Purchase Location', validators=[DataRequired()])
    date = DateTimeField('Purchase Date', default=datetime.utcnow)
    submit = SubmitField('Enter Data')