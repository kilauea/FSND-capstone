# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
import calendar
from datetime import date, datetime, timedelta
from sqlalchemy import extract, and_
from sqlalchemy.sql import func
from app import db
import json
from app.mod_base.base_model import Base

# Define a User model
class Calendar(Base):
    __tablename__ = 'calendar'
    id  = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    min_year = db.Column(db.SmallInteger, nullable=False, default=2000)
    max_year = db.Column(db.SmallInteger, nullable=False, default=2200)
    time_zone = db.Column(db.String(128), nullable=False, default="Europe/Madrid")  
    week_starting_day = db.Column(db.SmallInteger, nullable=False, default=0)      # 0: Monday, 6: Sunday
    emojis_enabled = db.Column(db.Boolean, nullable=False, default=True)
    auto_decorate_task_details_hyperlink = db.Column(db.Boolean, nullable=False, default=True)
    show_view_past_btn = db.Column(db.Boolean, nullable=False, default=True)
    hide_past_tasks = db.Column(db.Boolean, nullable=False, default=False)
    days_past_to_keep_hidden_tasks = db.Column(db.SmallInteger, nullable=False, default=62)
    # tasks = db.relationship(
    #     'Task',
    #     backref='list',
    #     lazy=True,
    #     cascade='all, delete, delete-orphan',
    #     passive_deletes=True,
    #     single_parent=True
    # )

    def __init__(
        self,
        id=None,
        name=None,
        description=None,
        min_year=None,
        max_year=None,
        time_zone=None,
        week_starting_day=None,
        emojis_enabled=None,
        show_view_past_btn=None,
        auto_decorate_task_details_hyperlink=True,
        hide_past_tasks=False,
        days_past_to_keep_hidden_tasks=62
    ):
        self.id  = id
        self.name = name
        self.description = description
        self.min_year = min_year
        self.max_year = max_year
        self.time_zone = time_zone 
        self.week_starting_day = week_starting_day
        self.emojis_enabled = emojis_enabled
        self.show_view_past_btn = show_view_past_btn
        self.auto_decorate_task_details_hyperlink = auto_decorate_task_details_hyperlink
        self.hide_past_tasks = hide_past_tasks
        self.days_past_to_keep_hidden_tasks = days_past_to_keep_hidden_tasks

    @staticmethod
    def month_names():
        return [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

    @staticmethod
    def month_name(month):
        return Calendar.month_names()[month - 1]

    @staticmethod
    def set_first_weekday(weekday):
        calendar.setfirstweekday(weekday)

    @staticmethod
    def weekdays(week_starting_day):
        weekdays_headers = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        ret = weekdays_headers[week_starting_day:] + weekdays_headers[0:week_starting_day]
        return ret

    @staticmethod
    def previous_month_and_year(year, month):
        previous_month_date = date(year, month, 1) - timedelta(days=2)
        return previous_month_date.month, previous_month_date.year

    @staticmethod
    def next_month_and_year(year, month):
        last_day_of_month = calendar.monthrange(year, month)[1]
        next_month_date = date(year, month, last_day_of_month) + timedelta(days=2)
        return next_month_date.month, next_month_date.year

    @staticmethod
    def current_date():
        today_date = datetime.date(datetime.now())
        return today_date.day, today_date.month, today_date.year

    @staticmethod
    def month_days(year, month):
        return calendar.Calendar(calendar.firstweekday()).itermonthdates(year, month)

    @staticmethod
    def month_days_with_weekday(year, month):
        return calendar.Calendar(calendar.firstweekday()).monthdayscalendar(year, month)

    '''
    insert()
        inserts a new model into a database
        the model must have a unique name
        the model must have a unique id or null id
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.insert()
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.delete()
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            drink.title = 'Black Coffee'
            drink.update()
    '''
    def update(self):
        db.session.commit()

class Task(Base):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendar.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    color = db.Column(db.String(32), nullable=False)
    details = db.Column(db.String(256), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=func.current_timestamp())
    end_time = db.Column(db.DateTime, nullable=False, default=func.current_timestamp())
    is_all_day = db.Column(db.Boolean, nullable=False, default=False)
    is_recurrent = db.Column(db.Boolean, nullable=False, default=False)
    repetition_value = db.Column(db.SmallInteger, nullable=False, default=0)
    repetition_type = db.Column(db.String(1), nullable=False, default="")
    repetition_subtype = db.Column(db.String(1), nullable=False, default="")

    def __init__(
        self,
        calendar_id=None,
        title=None,
        color=None,
        details=None,
        start_time=None,
        end_time=None,
        is_all_day=None,
        is_recurrent=None,
        repetition_value=None,
        repetition_type=None,
        repetition_subtype=None
    ):
        self.calendar_id = calendar_id
        self.title = title
        self.color = color
        self.details = details
        self.start_time = start_time
        self.end_time = end_time
        self.is_all_day = is_all_day
        self.is_recurrent = is_recurrent
        self.repetition_value = repetition_value
        self.repetition_type = repetition_type
        self.repetition_subtype = repetition_subtype

    '''
    short()
        short form representation of the Task model
    '''
    def short(self):
        return {
            'id': self.id,
            'title': self.title,
            'color': self.color,
            'start_time': self.start_time.strftime("%d/%m/%Y, %H:%M:%S"),
            'end_time' : self.end_time.strftime("%d/%m/%Y, %H:%M:%S")
        }

    '''
    long()
        long form representation of the Task model
    '''
    def long(self):
        return {
            'id': self.id,
            'calendar_id': self.calendar_id,
            'title': self.title,
            'color': self.color,
            'details': self.details,
            'start_time': self.start_time.strftime("%d/%m/%Y, %H:%M:%S"),
            'end_time': self.end_time.strftime("%d/%m/%Y, %H:%M:%S"),
            'is_all_day': self.is_all_day,
            'is_recurrent': self.is_recurrent,
            'repetition_value': self.repetition_value,
            'repetition_type': self.repetition_type,
            'repetition_subtype': self.repetition_subtype
        }

    def __repr__(self):
        return json.dumps(self.long())

    @staticmethod
    def _add_task_to_task_list(tasks_list, day, month, task, view_past_tasks=True):
        if not view_past_tasks:
            # Check if this task should be hidden
            start_time = datetime.now()
            task_end_time = datetime(start_time.year, month, day, task.end_time.hour, task.end_time.minute, task.end_time.second)
            if task_end_time < start_time:
                return
        if month not in tasks_list:
            tasks_list[month] = {}
        if day not in tasks_list[month]:
            tasks_list[month][day] = []
        tasks_list[month][day].append(task)

    @staticmethod
    def getTasks(calendar_id, year, month, view_past_tasks):
        tasks = {}
        if True:
            if view_past_tasks:
                m, y = Calendar.previous_month_and_year(year, month)
                start_time = datetime(y, m, 24)
            else:
                start_time = datetime.now()
            m, y = Calendar.next_month_and_year(year, month)
            end_time = datetime(y, m, 6)

            # Query and add non recurrent tasks
            tasks_query = Task.query.join(Calendar).filter(Task.calendar_id == calendar_id).filter(
                Task.is_recurrent == False,
                Task.end_time >= start_time,
                Task.start_time < end_time
            ).all()
            for task in tasks_query:
                task_day = task.start_time.day
                task_month = task.start_time.month
                Task._add_task_to_task_list(tasks, task_day, task_month, task)

            # Query and add recurrent tasks
            recurrent_tasks_query = Task.query.join(Calendar).filter(Task.calendar_id == calendar_id).filter(
                Task.is_recurrent == True,
                extract('year', Task.start_time) == year
            ).all()
            for task in recurrent_tasks_query:
                monthly_repetition_done = False
                for week in Calendar.month_days_with_weekday(year, month):
                    for weekday, day in enumerate(week):
                        if day == 0:
                            continue
                        if task.repetition_type == 'w':
                            # Weekly repetition: repetition_value is a week day
                            if task.repetition_value == weekday:
                                Task._add_task_to_task_list(tasks, day, month, task, view_past_tasks)
                        elif task.repetition_type == 'm':
                            if task.repetition_subtype == 'w':
                                # Monthly repetition: repetition_value is a week day
                                if task.repetition_value == weekday and not monthly_repetition_done:
                                    Task._add_task_to_task_list(tasks, day, month, task, view_past_tasks)
                                    monthly_repetition_done = True
                            elif task.repetition_subtype == 'm':
                                # Monthly repetition: repetition_value is a day
                                if task.repetition_value == day:
                                    Task._add_task_to_task_list(tasks, day, month, task, view_past_tasks)
        else:
            today = datetime.today()
            today = datetime(today.year, today.month, today.day)
            #last_day = Calendar.month_days(year, month)

            if view_past_tasks:
                past_tasks_query = Task.query.join(Calendar).filter(Task.calendar_id == calendar_id).filter(
                    Task.is_recurrent == False,
                    Task.start_time < today,
                    extract('year', Task.start_time) == year
                ).all()

                for el in past_tasks_query:
                    task_day = el.start_time.day
                    task_month = el.start_time.month
                    if task_month not in tasks:
                        tasks[task_month] = {}
                    if task_day not in tasks[task_month]:
                        tasks[task_month][task_day] = []
                    # tasks[str(month)][str(task_day)].append(el)
                    tasks[task_month][task_day].append(el)

            upcoming_tasks_query = Task.query.join(Calendar).filter(Task.calendar_id == calendar_id).filter(
                Task.is_recurrent == False,
                Task.start_time >= today,
                extract('year', Task.start_time) == year,
                extract('month', Task.start_time) == month
            ).all()
            #upcoming_tasks_query = Task.query.filter(Task.calendar_id == calendar_id).all()

            for el in upcoming_tasks_query:
                task_day = el.start_time.day
                task_month = el.start_time.month
                if task_month not in tasks:
                    tasks[task_month] = {}
                if task_day not in tasks[task_month]:
                    tasks[task_month][task_day] = []
                # tasks[str(month)][str(task_day)].append(el)
                tasks[task_month][task_day].append(el)

            recurrent_tasks_query = Task.query.join(Calendar).filter(Task.calendar_id == calendar_id).filter(
                Task.is_recurrent == True,
                extract('year', Task.start_time) == year
            ).all()

        return tasks

    # @staticmethod
    # def getTask(calendar_id, task_id, is_recurrent, year, month, day):
    #     if is_recurrent:
    #         tasks_query = Task.query.join(Calendar).filter(Task.calendar_id == calendar_id).filter(
    #             Task.id == task_id,
    #             Task.is_recurrent == is_recurrent
    #         ).all()
    #     else:
    #         tasks_query = Task.query.join(Calendar).filter(Task.calendar_id == calendar_id).filter(
    #             Task.id == task_id,
    #             extract('year', Task.start_time) == year,
    #             extract('month', Task.start_time) == month,
    #             extract('day', Task.start_time) == day
    #         ).all()
    #     if len(tasks_query) == 0:
    #         return None
    #     return vars(tasks_query[0])

    @staticmethod
    def getTask(task_id):
        return Task.query.get(task_id)

    '''
    insert()
        inserts a new model into a database
        the model must have a unique name
        the model must have a unique id or null id
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.insert()
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.delete()
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            drink.title = 'Black Coffee'
            drink.update()
    '''
    def update(self):
        db.session.commit()
