"""Initial migration.

Revision ID: 437ef732aa0e
Revises: 
Create Date: 2020-07-23 23:48:54.534407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '437ef732aa0e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auth_user',
    sa.Column('date_created', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('date_modified', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('password', sa.String(length=192), nullable=False),
    sa.Column('role', sa.SmallInteger(), nullable=False),
    sa.Column('status', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.execute("INSERT INTO auth_user \
(name, email, password, role, status) \
VALUES \
('Arturo Crespo', 'acrespodelavina@yahoo.es', 'wedq34ewfa34fwefawef34f34fa4wf', 0, 1)")

    op.create_table('calendar',
    sa.Column('date_created', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('date_modified', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('description', sa.String(length=256), nullable=False),
    sa.Column('min_year', sa.SmallInteger(), nullable=False),
    sa.Column('max_year', sa.SmallInteger(), nullable=False),
    sa.Column('time_zone', sa.String(length=128), nullable=False),
    sa.Column('week_starting_day', sa.SmallInteger(), nullable=False),
    sa.Column('emojis_enabled', sa.Boolean(), nullable=False),
    sa.Column('auto_decorate_task_details_hyperlink', sa.Boolean(), nullable=False),
    sa.Column('show_view_past_btn', sa.Boolean(), nullable=False),
    sa.Column('hide_past_tasks', sa.Boolean(), nullable=False),
    sa.Column('days_past_to_keep_hidden_tasks', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.execute("INSERT INTO calendar \
(name, description, min_year, max_year, time_zone, week_starting_day, \
emojis_enabled, auto_decorate_task_details_hyperlink, show_view_past_btn, hide_past_tasks, \
days_past_to_keep_hidden_tasks) \
VALUES \
('Main floor calendar', 'Main floor emplyees calendar', 2000, 2200, 'Europe/Madrid', 0, \
'TRUE', 'TRUE', 'TRUE', 'FALSE', \
62)")

    op.create_table('task',
    sa.Column('date_created', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('date_modified', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('calendar_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=False),
    sa.Column('color', sa.String(length=32), nullable=False),
    sa.Column('details', sa.String(length=256), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False, default=sa.func.now()),
    sa.Column('end_time', sa.DateTime(), nullable=False, default=sa.func.now()),
    sa.Column('is_all_day', sa.Boolean(), nullable=False),
    sa.Column('is_recurrent', sa.Boolean(), nullable=False),
    sa.Column('repetition_value', sa.SmallInteger(), nullable=False),
    sa.Column('repetition_type', sa.String(length=1), nullable=False),
    sa.Column('repetition_subtype', sa.String(length=1), nullable=False),
    sa.ForeignKeyConstraint(['calendar_id'], ['calendar.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['auth_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.execute("INSERT INTO task \
(calendar_id, user_id, title, color, details, start_time, end_time, \
is_all_day, is_recurrent, repetition_value, repetition_type, repetition_subtype) \
VALUES \
(1, 1, 'Task 1', '#B19CDA', 'Shift 1 task', '2020-06-30', '2020-06-30', \
'TRUE', 'TRUE', 1, 'm', 'm')")
    op.execute("INSERT INTO task \
(calendar_id, user_id, title, color, details, start_time, end_time, \
is_all_day, is_recurrent, repetition_value, repetition_type, repetition_subtype) \
VALUES \
(1, 1, 'Task 2', '#B19CDA', 'Shift 2 task', '2020-07-25', '2020-07-25', \
'TRUE', 'FALSE', 0, ' ', ' ')")
    op.execute("INSERT INTO task \
(calendar_id, user_id, title, color, details, start_time, end_time, \
is_all_day, is_recurrent, repetition_value, repetition_type, repetition_subtype) \
VALUES \
(1, 1, 'Final project date', '#B19CDA', 'FSND final project last day', '2020-07-30', '2020-07-30', \
'TRUE', 'FALSE', 0, ' ', ' ')")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task')
    op.drop_table('calendar')
    op.drop_table('auth_user')
    # ### end Alembic commands ###
