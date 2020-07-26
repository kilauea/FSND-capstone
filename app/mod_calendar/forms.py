from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, DateField, BooleanField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, AnyOf, URL, Length, Regexp, Optional
from app.mod_calendar.models import Task

class TaskForm(FlaskForm):
    #start = datetime.now()
    #end = start + timedelta(hours=8)

    calendar_id = HiddenField('calendar_id')
    user_id = HiddenField('user_id')
    title = StringField('Title', validators=[DataRequired(), Length(max=128)], render_kw={'autofocus': True})
    color = StringField('Color', validators=[Length(max=32)])
    details = TextAreaField('Details', validators=[Length(max=256)])
    start_date = DateField('Start date', format='%d/%m/%Y', validators=[DataRequired()])
    start_time = DateTimeField('Start time', format='%H:%M:%S', validators=[DataRequired()])
    end_date = DateField('End date', format='%d/%m/%Y', validators=[DataRequired()])
    end_time = DateTimeField('End time', format='%H:%M:%S', validators=[DataRequired()])
    is_all_day = BooleanField('All day event', default=False, false_values={False, 'false', ''})
    is_recurrent = BooleanField('Recurrent', default=False, false_values={False, 'false', ''})
    repetition_value = StringField('Repetition value', validators=[Length(max=1)])
    repetition_type = StringField('Repetition type', validators=[Length(max=1)])
    repetition_subtype = StringField('Repetition sub-type', validators=[Length(max=1)])
