def calculate_cpf(age, total_wages):
    ow = total_wages  # Assuming Ordinary Wages = Total Wages
    aw = 0  # No data provided for Additional Wages

    # Set rates and thresholds based on age
    if age <= 55:
        thresholds = [50, 500, 750]
        rates = [0.17, 0.6]
        max_total_cpf = [0, 0, 37 / 100 * ow, 2220 + 37 / 100 * aw]
        max_employee_cpf = [0, 0, 20 / 100 * ow, 1200 + 20 / 100 * aw]
    elif age <= 60:
        thresholds = [50, 500, 750]
        rates = [0.145, 0.45]
        max_total_cpf = [0, 0, 29.5 / 100 * ow, 1770 + 29.5 / 100 * aw]
        max_employee_cpf = [0, 0, 15 / 100 * ow, 900 + 15 / 100 * aw]
    elif age <= 65:
        thresholds = [50, 500, 750]
        rates = [0.11, 0.285]
        max_total_cpf = [0, 0, 20.5 / 100 * ow, 1230 + 20.5 / 100 * aw]
        max_employee_cpf = [0, 0, 9.5 / 100 * ow, 570 + 9.5 / 100 * aw]
    elif age <= 70:
        thresholds = [50, 500, 750]
        rates = [0.085, 0.21]
        max_total_cpf = [0, 0, 15.5 / 100 * ow, 930 + 15.5 / 100 * aw]
        max_employee_cpf = [0, 0, 7 / 100 * ow, 420 + 7 / 100 * aw]
    else:  # age > 70
        thresholds = [50, 500, 750]
        rates = [0.075, 0.15]
        max_total_cpf = [0, 0, 12.5 / 100 * ow, 750 + 12.5 / 100 * aw]
        max_employee_cpf = [0, 0, 5 / 100 * ow, 300 + 5 / 100 * aw]

    # Calculate contribution
    if total_wages <= thresholds[0]:
        total_cpf = max_total_cpf[0]
        employee_share = max_employee_cpf[0]
    elif total_wages <= thresholds[1]:
        total_cpf = total_wages * rates[0]
        employee_share = max_employee_cpf[1]
    elif total_wages <= thresholds[2]:
        total_cpf = thresholds[1] * rates[0] + (total_wages - thresholds[1]) * rates[1]
        employee_share = (total_wages - thresholds[1]) * rates[1]
    else:
        total_cpf = min(max_total_cpf[2], max_total_cpf[3])
        employee_share = min(max_employee_cpf[2], max_employee_cpf[3])

        # Calculate employer's share
        employer_share = total_cpf - employee_share

        # Round down to the nearest dollar
        total_cpf = int(total_cpf)
        employee_share = int(employee_share)
        employer_share = int(employer_share)

        return total_cpf, employee_share, employer_share


print(calculate_cpf(61, 1400))
