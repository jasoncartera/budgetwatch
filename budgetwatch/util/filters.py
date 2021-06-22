from budgetwatch import app
from datetime import datetime
from pytz import timezone

def pacific_time(date):
    """ Converts UTC to Pacific """
    return date.astimezone(timezone('US/Pacific')).strftime('%m/%d/%Y')
  
app.add_template_filter(pacific_time)