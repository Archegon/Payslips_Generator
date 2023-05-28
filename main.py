import json
import os
import random
import string

from datetime import datetime, date

from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

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
        end_month = form.end_month_year.data

        return render_template('payslipinput.html', employee_id=employee_id, start_month=start_month,
                               end_month=end_month)

    return render_template('payslipinput.html', form=form)


@app.route('/preview_payslip/<employee_id>/<start_month>/<end_month>')
def preview_payslip(employee_id, start_month, end_month):
    saved_employees = employee_save.load()
    employee = saved_employees.get(employee_id)

    age = calculate_age(employee['Date of Birth'])
    payslip_id = generate_payslip_id(6)

    # Package the parameters into a dictionary
    template_parameters = {
        'employee_name': employee['Name'],
        'employee_id': employee_id,
        'employee_dob': employee['Date of Birth'],
        'employee_age': age,
        'employee_position': employee['Position'],
        'employee_salary': employee['Salary'],
        'total_income': employee['Salary'],
        'payslip_id': payslip_id,
        'start_month': start_month,
        'end_month': end_month
    }

    # Pass the dictionary to the template
    return render_template('generated_payslip.html', **template_parameters)


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
