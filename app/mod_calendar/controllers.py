import sys
from flask import Blueprint, abort, current_app, g, jsonify, make_response, redirect, render_template, request
from datetime import date, datetime, timedelta
import re

from app.mod_calendar.models import Calendar
from app.mod_calendar.models import Task
from app.mod_calendar.forms import TaskForm

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_calendar = Blueprint('calendar', __name__, url_prefix='/calendar')

@mod_calendar.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', error_msg=error), 404

@mod_calendar.errorhandler(422)
def unprocessable_entity_error(error):
    return render_template('errors/422.html', error_msg=error), 422

@mod_calendar.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html', error_msg=error), 500

def previous_month_link(calendar_id, year, month):
    calendar_query = Calendar.query.get(calendar_id)
    month, year = Calendar.previous_month_and_year(year=year, month=month)
    return (
        ""
        if year < calendar_query.min_year or year > calendar_query.max_year
        else "?y={}&m={}".format(year, month)
    )

def next_month_link(calendar_id, year, month):
    calendar_query = Calendar.query.get(calendar_id)
    month, year = Calendar.next_month_and_year(year=year, month=month)
    return (
        ""
        if year < calendar_query.min_year or year > calendar_query.max_year
        else "?y={}&m={}".format(year, month)
    )

@mod_calendar.route('/<int:calendar_id>/', methods=['GET'])
def show_calendar(calendar_id):
    calendar_query = Calendar.query.get(calendar_id)
    if calendar_query is None:
        return not_found_error('Calendar %s not found' % calendar_id)

    Calendar.set_first_weekday(calendar_query.week_starting_day)

    current_day, current_month, current_year = Calendar.current_date()
    year = int(request.args.get("y", current_year))
    year = max(min(year, calendar_query.max_year), calendar_query.min_year)
    month = int(request.args.get("m", current_month))
    month = max(min(month, 12), 1)
    month_name = Calendar.month_name(month)

    if calendar_query.hide_past_tasks:
        view_past_tasks = False
    else:
        view_past_tasks = request.cookies.get("ViewPastTasks", "1") == "1"

    tasks = Task.getTasks(calendar_id, year, month, view_past_tasks)

    weekdays_headers = Calendar.weekdays(calendar_query.week_starting_day)
    month_days = Calendar.month_days(year, month)

    return render_template(
        "calendar/calendar.html",
        calendar_id=calendar_id,
        year=year,
        month=month,
        month_name=month_name,
        current_year=current_year,
        current_month=current_month,
        current_day=current_day,
        month_days=Calendar.month_days(year, month),
        previous_month_link=previous_month_link(calendar_id, year, month),
        next_month_link=next_month_link(calendar_id, year, month),
        tasks=tasks,
        display_view_past_button=calendar_query.show_view_past_btn,
        weekdays_headers=weekdays_headers
    )

@mod_calendar.route('/<int:calendar_id>/<int:year>/<int:month>/new_task', methods=['GET'])
def new_task(calendar_id, year, month):
    calendar_query = Calendar.query.get(calendar_id)
    if calendar_query is None:
        return not_found_error('Calendar %s not found' % calendar_id)

    Calendar.set_first_weekday(calendar_query.week_starting_day)

    current_day, current_month, current_year = Calendar.current_date()
    year = max(min(year, calendar_query.max_year), calendar_query.min_year)
    month = max(min(month, 12), 1)

    if current_month == month and current_year == year:
        day = current_day
    else:
        day = 1
    day = int(request.args.get("day", day))

    start_time = datetime(year, month, day)
    end_time = start_time + timedelta(hours=23, minutes=59, seconds=59)
    task = Task(
        calendar_id=calendar_id,
        user_id=1,
        title='',
        color=current_app.config["BUTTON_CUSTOM_COLOR_VALUE"],
        details='',
        start_time=start_time,
        end_time=end_time,
        is_all_day=True,
        is_recurrent=False,
        repetition_value=0,
        repetition_type='',
        repetition_subtype=''
    )

    taskForm = TaskForm()
    taskForm.calendar_id.default = calendar_id
    taskForm.user_id.default = 1
    taskForm.title.default = ''
    taskForm.color.default = current_app.config["BUTTON_CUSTOM_COLOR_VALUE"]
    taskForm.details.default = ''
    taskForm.start_date.default = start_time.strftime("%H:%M:%S")
    taskForm.start_time.default = start_time.strftime("%d/%m/%Y")
    taskForm.end_date.default = end_time.strftime("%H:%M:%S")
    taskForm.end_time.default = end_time.strftime("%d/%m/%Y")
    taskForm.is_all_day.default = True
    taskForm.is_recurrent.default = False
    taskForm.repetition_value.default = 0
    taskForm.repetition_type.default = ''
    taskForm.repetition_subtype.default = ''

    return render_template(
        "calendar/task.html",
        form=taskForm,
        calendar_id=calendar_id,
        year=year,
        month=month,
        min_year=calendar_query.min_year,
        max_year=calendar_query.max_year,
        month_names=Calendar.month_names(),
        task=vars(task),
        editing=False,
        emojis_enabled=calendar_query.emojis_enabled,
        button_default_color_value=current_app.config["BUTTON_CUSTOM_COLOR_VALUE"],
        buttons_colors=current_app.config["BUTTONS_COLORS_LIST"],
        buttons_emojis=current_app.config["BUTTONS_EMOJIS_LIST"] if calendar_query.emojis_enabled else tuple(),
    )

@mod_calendar.route('/<int:calendar_id>/new_task', methods=['POST'])
def save_task(calendar_id):
    title = request.form["title"].strip()
    start_date = request.form.get("start_date", "")
    end_date = request.form.get("end_date", "")

    if len(start_date) > 0 and len(end_date) > 0:
        date_fragments = start_date.split('-')
        year = int(date_fragments[0])
        month = int(date_fragments[1])
        day = int(date_fragments[2])

        is_all_day = request.form.get("is_all_day", "0") == "1"
        start_time = request.form["start_time"]
        end_time = request.form.get("end_time", None)
        details = request.form["details"].replace("\r", "").replace("\n", "<br>")
        color = request.form["color"]
        is_recurrent = request.form.get("repeats", "0") == "1"
        repetition_type = request.form.get("repetition_type")
        repetition_subtype = request.form.get("repetition_subtype")
        repetition_value = int(request.form["repetition_value"])

        newTask = Task(
            calendar_id=calendar_id,
            user_id=1,
            title=title,
            color=color,
            details=details,
            start_time=datetime.strptime('%s %s' % (start_date, start_time), '%Y-%m-%d %H:%M'),
            end_time=datetime.strptime('%s %s' % (end_date, end_time), '%Y-%m-%d %H:%M'),
            is_all_day=is_all_day,
            is_recurrent=is_recurrent,
            repetition_value=repetition_value,
            repetition_type=repetition_type,
            repetition_subtype=repetition_subtype
        )
        newTask.insert()
        return redirect("/calendar/%s/?y=%d&m=%d" % (calendar_id, year, month), code=302)
    else:
        return redirect("/calendar/%s" % (calendar_id), code=302)

@mod_calendar.route('/<int:calendar_id>/<int:year>/<int:month>/<int:day>/<int:task_id>', methods=['GET'])
def edit_task(calendar_id, year, month, day, task_id):
    calendar_query = Calendar.query.get(calendar_id)
    if calendar_query is None:
        return not_found_error('Calendar %s not found' % calendar_id)

    repeats = request.args.get("repeats") == "1"
    task = Task.getTask(task_id)
    if task == None:
        return not_found_error('Task %s not found' % task_id)

    if task.details == "&nbsp;":
        task.details = ""

    taskForm = TaskForm()
    taskForm.calendar_id.default = task.calendar_id
    taskForm.user_id.default = task.user_id
    taskForm.title.default = task.title
    taskForm.color.default = task.color
    taskForm.details.default = task.details
    taskForm.start_date.default = task.start_time.date
    taskForm.start_time.default = task.start_time.time
    taskForm.end_date.default = task.end_time.date
    taskForm.end_time.default = task.end_time.time
    taskForm.is_all_day.default = task.is_all_day
    taskForm.is_recurrent.default = task.is_recurrent
    taskForm.repetition_value.default = task.repetition_value
    taskForm.repetition_type.default = task.repetition_type
    taskForm.repetition_subtype.default = task.repetition_subtype
    taskForm.process()

    return render_template(
        "calendar/task.html",
        form=taskForm,
        calendar_id=calendar_id,
        year=year,
        month=month,
        day=day,
        min_year=calendar_query.min_year,
        max_year=calendar_query.max_year,
        month_names=Calendar.month_names(),
        task=vars(task),
        editing=True,
        emojis_enabled=calendar_query.emojis_enabled,
        button_default_color_value=current_app.config["BUTTON_CUSTOM_COLOR_VALUE"],
        buttons_colors=current_app.config["BUTTONS_COLORS_LIST"],
        buttons_emojis=current_app.config["BUTTONS_EMOJIS_LIST"] if calendar_query.emojis_enabled else tuple(),
    )

@mod_calendar.route('/<int:calendar_id>/task/<int:task_id>', methods=['POST'])
def update_task(calendar_id, task_id):
    title = request.form["title"].strip()
    color = request.form["color"]
    details = request.form["details"].replace("\r", "").replace("\n", "<br>")
    start_date = request.form["start_date"]
    start_time = request.form["start_time"]
    end_date = request.form["end_date"]
    end_time = request.form["end_time"]
    is_all_day = request.form.get("is_all_day", "0") == "1"
    is_recurrent = request.form.get("repeats", "0") == "1"
    repetition_value = int(request.form["repetition_value"])
    repetition_type = request.form.get("repetition_type", "")
    repetition_subtype = request.form.get("repetition_subtype", "")

    try:
        task = Task.getTask(task_id)
        if task == None:
            return not_found_error('Task %s not found' % task_id)

        task.calendar_id = calendar_id
        task.user_id = 1
        task.title = title
        task.color = color
        task.details = details
        task.start_time = datetime.strptime('%s %s' % (start_date, start_time), '%Y-%m-%d %H:%M')
        task.end_time = datetime.strptime('%s %s' % (end_date, end_time), '%Y-%m-%d %H:%M')
        task.is_all_day = is_all_day
        task.is_recurrent = is_recurrent
        task.repetition_value = repetition_value
        task.repetition_type = repetition_type
        task.repetition_subtype = repetition_subtype

        task.update()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return unprocessable_entity_error('Task %s not saved' % task_id)

    return redirect("/calendar/%d?y=%d&m=%d" % (calendar_id, task.start_time.year, task.start_time.month), code=302)

@mod_calendar.route('/<int:calendar_id>/task/<int:task_id>', methods=['PATCH'])
def update_task_day(calendar_id, task_id):
    body = request.get_json()
    newDay = int(body.get('newDay'))
    try:
        task = Task.getTask(task_id)
        if task == None:
            return not_found_error('Task %s not found' % task_id)
        if newDay:
            task.start_time = task.start_time.replace(day = newDay)
            task.end_time = task.end_time.replace(day = newDay)
            task.update()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return unprocessable_entity_error('Task %s not saved' % task_id)

    return jsonify({
      'success': True,
      'task_id': task_id
    })

@mod_calendar.route('/<int:calendar_id>/task/<int:task_id>', methods=['DELETE'])
def delete_task(calendar_id, task_id):
    try:
        task = Task.getTask(task_id)
        if task == None:
            return not_found_error('Task %s not found' % task_id)
        task.delete()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return unprocessable_entity_error('Task %s not saved' % task_id)

    return jsonify({
      'success': True,
      'task_id': task_id
    })
