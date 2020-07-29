from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, SelectMultipleField,
    DateTimeField, DateField, BooleanField,
    TextAreaField, HiddenField, IntegerField
)
from wtforms.validators import (
    DataRequired, AnyOf, URL,
    Length, Regexp, Optional,
    NumberRange
)
from app.mod_calendar.models import Calendar, Task

class CalendarForm(FlaskForm):
    calendar_id = HiddenField('calendar_id')
    name = StringField('Name', validators=[DataRequired(), Length(max=128)], render_kw={'autofocus': True})
    description = TextAreaField('Description', validators=[Length(max=256)])
    min_year = IntegerField('Minimum calendar year', default = 1900, validators=[DataRequired(), NumberRange(min=1900, max=2200)])
    max_year = IntegerField('Maximum calendar year', default = 2200, validators=[DataRequired(), NumberRange(min=1900, max=2200)])
    time_zone = StringField('Time Zone', default="Europe/Madrid", validators=[DataRequired(), Length(max=128)])
    week_starting_day = SelectField('Week Starting Day',
        choices = [
            ('0', 'Monday'),
            ('1', 'Tuesday'),
            ('2', 'Wednesday'),
            ('3', 'Thursday'),
            ('4', 'Friday'),
            ('5', 'Saturday'),
            ('6', 'Sunday')
        ], validators=[DataRequired()])
    emojis_enabled = BooleanField('Enable Emojis', default=True, false_values={False, 'false', ''})
    show_view_past_btn = BooleanField('Show View Past Button', default=True, false_values={False, 'false', ''})

class TaskForm(FlaskForm):
    task_id = HiddenField('task_id')
    calendar_id = HiddenField('calendar_id')
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
