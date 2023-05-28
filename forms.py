from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, FileField, SelectField
from wtforms.validators import DataRequired
from datetime import date, datetime


class EmployeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    id = StringField('NRIC/FIN', id='id', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    dob = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    salary = StringField('Salary', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CompanyForm(FlaskForm):
    name = StringField('Company Name', validators=[DataRequired()])
    uen = StringField('UEN', validators=[DataRequired()])
    address = StringField('Company Address', validators=[DataRequired()])
    logo = FileField('Company Logo')
    submit = SubmitField('Save')


class PayslipForm(FlaskForm):
    employee = SelectField('Employee', choices=[], validators=[DataRequired()])
    start_month_year = DateField('Start Month/Year', format='%m/%Y', validators=[DataRequired()])
    submit = SubmitField('Generate Payslip')

    def validate_end_month_year(self, end_month_year):
        if end_month_year.data < self.start_month_year.data:
            raise ValidationError('End Month/Year must not be earlier than Start Month/Year.')
