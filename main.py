import json
import os
import random
import string

from calendar import monthrange

from datetime import datetime, date

from flask import Flask, render_template, request, flash, redirect, url_for, send_file, render_template_string
from werkzeug.utils import secure_filename

from calculate_cpf import calculate_cpf
from forms import CompanyForm, PayslipForm, EmployeeForm
from save import Savefile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'whatisupdudes'
app.config['UPLOAD_FOLDER'] = 'company_assets'

employee_save = Savefile('employees.json')
company_save = Savefile('company.json')


def calculate_age(birthdate_str):
    # Convert string to date object
    birthdate = datetime.strptime(birthdate_str, "%d-%m-%Y").date()

    # Calculate age
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    return age


def generate_payslip_id(length=6):
    # Define the characters that can be used in the payslip ID
    letters = string.ascii_uppercase
    numbers = string.digits

    # Generate a random payslip ID
    payslip_id = ''.join(random.choice(letters) for _ in range(length - 4))
    payslip_id += ''.join(random.choice(numbers) for _ in range(4))

    return payslip_id


@app.route('/')
def home():
    employee_data = employee_save.load()
    company_name = company_save.load()['name']

    return render_template('home.html', employee_data=employee_data, company_name=company_name)


@app.route('/new_payslip', methods=['GET', 'POST'])
def new_payslip():
    form = PayslipForm()

    saved_employees = employee_save.load()

    # Update the choices of the 'employee' field with the loaded employee data
    form.employee.choices = [(id, employee['Name']) for id, employee in saved_employees.items()]

    if form.validate_on_submit():
        flash("Payslip submitted successfully!")

        # Extract the form data
        employee_id = form.employee.data
        start_month = form.start_month_year.data

        return render_template('payslipinput.html', employee_id=employee_id, start_month=start_month)

    return render_template('payslipinput.html', form=form)


@app.route('/preview_payslip/<employee_id>/<start_month>/<overtime_pay>/<allowance_pay>')
def preview_payslip(employee_id, start_month, overtime_pay, allowance_pay):
    saved_employees = employee_save.load()
    company = company_save.load()
    employee = saved_employees.get(employee_id)
    overtime_pay = float(overtime_pay)
    allowance_pay = float(allowance_pay)

    # Convert to datetime object
    start_month_datetime = datetime.strptime(start_month, "%Y-%m-%d")

    # Extract month name
    payroll_month = start_month_datetime.strftime("%B %Y")

    # Convert to datetime objects
    start_month_datetime = datetime.strptime(start_month, "%Y-%m-%d")
    end_month_datetime = datetime.strptime(start_month, "%Y-%m-%d")

    # Get the last day of the end_month
    _, last_day = monthrange(end_month_datetime.year, end_month_datetime.month)

    # Set the day to 1 for the start_month and to the last day for the end_month
    start_period = start_month_datetime.replace(day=1).strftime("%d %b %Y")  # "01 January 2023"
    end_period = end_month_datetime.replace(day=last_day).strftime("%d %b %Y")
    payment_date = end_period

    age = calculate_age(employee['Date of Birth'])
    payslip_id = generate_payslip_id(6)

    # Check if the employee_id starts with "G"
    if employee_id.startswith('G'):
        employee_cpf = 0
        employer_cpf = 0
    else:
        cpf = calculate_cpf(age, int(employee['Salary']))
        employee_cpf = cpf[1]
        employer_cpf = cpf[2]

    # Convert the string values to float or decimal
    employee_salary = float(employee['Salary'])
    employee_cpf = float(employee_cpf)
    employer_cpf = float(employer_cpf)
    total_deduction = float(employee_cpf)
    total_income = float(employee['Salary']) + overtime_pay + allowance_pay

    # Net pay calculation
    net_pay = total_income - total_deduction

    # Package the parameters into a dictionary
    template_parameters = {
        'company_name': company['name'],
        'company_address': company['address'],
        'company_uen': company['uen'],
        'employee_name': employee['Name'],
        'employee_id': employee_id,
        'employee_dob': employee['Date of Birth'],
        'employee_age': age,
        'employee_position': employee['Position'],
        'payslip_month': payroll_month,
        'payslip_startdate': start_period,
        'payslip_enddate': end_period,
        'payment_date': payment_date,
        'employee_salary': "{:.2f}".format(employee_salary),
        'employee_cpf': "{:.2f}".format(employee_cpf),
        'employer_cpf': "{:.2f}".format(employer_cpf),
        'total_deduction': "{:.2f}".format(total_deduction),
        'total_income': "{:.2f}".format(total_income),
        'net_pay': "{:.2f}".format(net_pay),
        'payslip_id': payslip_id,
        'start_month': start_month,
        'overtime_pay': "{:.2f}".format(overtime_pay),
        'allowance_pay': "{:.2f}".format(allowance_pay)
    }

    payslip_html = render_template_string(open("templates/generated_payslip.html").read(), **template_parameters)

    with open('templates/temp_payslip.html', 'w') as file:
        file.write(payslip_html)

    # Pass the dictionary to the template
    return render_template('generated_payslip.html', **template_parameters)


@app.route('/download_payslip', methods=['GET'])
def download_payslip():
    html_path = 'temp_payslip.html'
    return render_template(html_path)


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    form = EmployeeForm()

    if form.validate_on_submit():
        employee_data = {
            form.id.data.upper(): {
                'Name': form.name.data,
                'Position': form.position.data,
                'Date of Birth': form.dob.data.strftime("%d-%m-%Y"),
                'Salary': form.salary.data
            }
        }

        employee_save.update(employee_data)

        flash("Form submitted successfully!")
    else:
        print(request.form)

    print(form.errors)
    return render_template('employeeinput.html', form=form)


@app.route('/employee/edit/<employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    form = EmployeeForm()
    employee_data = employee_save.load().get(employee_id)

    if not employee_data:
        flash('Employee not found', 'error')
        return redirect(url_for('home'))

    if form.validate_on_submit():
        employee_data['Name'] = form.name.data
        employee_data['Position'] = form.position.data
        employee_data['Date of Birth'] = form.dob.data.strftime("%d-%m-%Y")
        employee_data['Salary'] = form.salary.data

        employee_save.update({employee_id: employee_data})

        flash('Employee information updated successfully', 'success')
        return redirect(url_for('home'))

    form.name.data = employee_data['Name']
    form.id.data = employee_id
    form.position.data = employee_data['Position']
    form.dob.data = datetime.strptime(employee_data['Date of Birth'], "%d-%m-%Y")
    form.salary.data = employee_data['Salary']

    return render_template('employeeinput.html', form=form, employee_id=employee_id)


@app.route('/edit_company_info', methods=['GET', 'POST'])
def edit_company_info():
    existing_data = company_save.load()
    form = CompanyForm()

    form.name.data = existing_data['name']
    form.uen.data = existing_data['uen']
    form.address.data = existing_data['address']

    if form.validate_on_submit():
        logo = form.logo.data  # Get the logo FileStorage object

        if logo:
            # Save the logo image to a file
            filename = secure_filename("logo.png")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            logo.save(file_path)

        company_data = {
            'name': form.name.data,
            'uen': form.uen.data,
            'address': form.address.data
        }

        company_save.update(company_data)

        flash("Company information updated successfully!")
        return redirect(url_for('home'))

    print(form.errors)
    return render_template('companyinput.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
