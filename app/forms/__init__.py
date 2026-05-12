from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])


class TaskForm(FlaskForm):
    assigned_to = SelectField('Assign To', coerce=int, validators=[DataRequired()])
    task_description = TextAreaField('Task Description', validators=[DataRequired(), Length(min=5)])
    status = SelectField('Status', choices=[
        ('assigned', 'Assigned'),
        ('done', 'Done')
    ], default='assigned')


class VisitorLogForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=11)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    purpose_of_visit = TextAreaField('Purpose of Visit', validators=[DataRequired(), Length(min=3)])