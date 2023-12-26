from datetime import datetime

from bson import ObjectId
from flask import Flask, request, render_template, session, redirect
import pymongo

app = Flask(__name__)
app.secret_key = "payroll"
my_client = pymongo.MongoClient("mongodb://localhost:27017")
my_db = my_client["payroll"]
admin_collection = my_db["admin"]
employee_collection = my_db["employee"]
tax_collection = my_db["tax"]
payrol_col = my_db['Payrol']
leaves_col = my_db['leaves']
extra_allowances_col = my_db['extra_allowance']
deduction_col = my_db['deduction']
time_sheet_col = my_db['time_sheet']
salary_report_col = my_db['salary_report']

count = admin_collection.count_documents({})
if count == 0:
    admin_collection.insert_one({"name": "admin","email": "admin@gmail.com", "password": "admin"})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/admin_login1", methods=['post'])
def admin_login1():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email" : email, "password" : password}
    count = admin_collection.count_documents(query)
    if count > 0:
        session['role'] = 'admin'
        return redirect("/admin_home")
    else:
        return render_template("mssg.html", message="Invalid Login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/add_employee")
def add_employee():
    return render_template("add_employee.html")


@app.route("/add_employee1", methods=['post'])
def add_employee1():
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    dob = request.form.get("dob")
    phone = request.form.get("phone")
    gender = request.form.get("gender")
    address = request.form.get("address")
    department = request.form.get("department")
    password = request.form.get("password")
    employement_start_date = request.form.get("employement_start_date")
    bank_info = request.form.get("bank_info")
    account_type = request.form.get("account_type")
    wage_type = request.form.get("wage_type")
    income = request.form.get("income")
    query = {"phone": phone, "email": email}
    count = employee_collection.count_documents(query)
    if count > 0:
        return render_template("mssg.html", message="Duplicate Phone Number")
    query = {"firstname": firstname, "lastname": lastname, "dob": dob, "phone": phone,  "address": address,
                "department": department, "employement_start_date": employement_start_date, "bank_info": bank_info,
                "wage_type": wage_type, "email": email, "password": password, "account_type": account_type, "gender": gender}
    result = employee_collection.insert_one(query)
    employee_id = result.inserted_id
    yearly_pay_frequency = request.form.get("yearly_pay_frequency")
    hourly_wage = request.form.get("hourly_wage")
    if wage_type == 'salary_based':
        query = {"employee_id": ObjectId(employee_id), "income": income, "yearly_pay_frequency": yearly_pay_frequency}
    elif wage_type == 'hour_based':
        query = {"employee_id": ObjectId(employee_id), "hourly_wage": hourly_wage}
    payrol_col.insert_one(query)
    return render_template("mssg.html", message="Details Added Successfully")


@app.route("/view_employee")
def view_employee():
    employees = employee_collection.find({})
    return render_template("view_employee.html", employees=employees, get_pay_salary=get_pay_salary)


@app.route("/modify_employee")
def modify_employee():
    employee_id = request.args.get("employee_id")
    query = {"_id": ObjectId(employee_id)}
    employee = employee_collection.find_one(query)
    return render_template("modify_employee.html",employee_id=employee_id, employee=employee)


@app.route("/modify_employee1", methods=['post'])
def modify_employee1():
    employee_id = request.form.get("employee_id")
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    dob = request.form.get("dob")
    phone = request.form.get("phone")
    address = request.form.get("address")
    department = request.form.get("department")
    employement_start_date = request.form.get("employement_start_date")
    bank_info = request.form.get("bank_info")
    wage_type = request.form.get("wage_type")
    query1 = {"_id": ObjectId(employee_id)}
    query2 = {"$set": {"firstname":firstname, "lastname":lastname, "dob":dob, "phone":phone, "address":address,
                        "department":department, "employement_start_date":employement_start_date, "bank_info":bank_info,
                        "wage_type":wage_type}}
    employee_collection.update_one(query1, query2)
    return redirect("/view_employee")


@app.route("/tax_info")
def tax_info():
    taxs = tax_collection.find()
    return render_template("tax_info.html",taxs=taxs)


@app.route("/add_tax")
def add_tax():
    return render_template("add_tax.html")


@app.route("/add_tax1", methods=['post'])
def add_tax1():
    tax_type = request.form.get("tax_type")
    tax_amount = request.form.get("tax_amount")
    query = {"tax_type": tax_type, "tax_amount": tax_amount}
    tax_collection.insert_one(query)
    return redirect("/tax_info")


@app.route("/pay_salary")
def pay_salary():
    employee_id = request.args.get("employee_id")
    query = {"_id": ObjectId(employee_id)}
    employee = employee_collection.find_one(query)
    return render_template("pay_salary.html", employee_id=employee_id, employee=employee)


@app.route("/pay_salary1", methods=['post'])
def pay_salary1():
    query = {}
    employee_id = request.form.get("employee_id")
    wage_type = request.form.get("wage_type")
    salary = request.form.get("salary")
    pay_frequency = request.form.get("pay_frequency")
    hourly_wage = request.form.get("hourly_wage")
    if wage_type == 'salary_based':
        query = {"employee_id": ObjectId(employee_id), "salary": salary, "pay_frequency": pay_frequency}
    elif wage_type == 'hour_based':
        query = {"employee_id": ObjectId(employee_id), "hourly_wage": hourly_wage}
    payrol_col.insert_one(query)
    return redirect("/view_employee")


@app.route("/extra_allowances")
def extra_allowances():
    allowances = extra_allowances_col.find()
    return render_template("extra_allowances.html", allowances=allowances)


@app.route("/add_extra_allowances")
def add_extra_allowances():
    return render_template("add_extra_allowances.html")


@app.route("/add_extra_allowances1", methods=['post'])
def add_extra_allowances1():
    bonus = request.form.get("bonus")
    insurance = request.form.get("insurance")
    query = {"insurance": insurance, "bonus": bonus}
    extra_allowances_col.insert_one(query)
    return redirect("/extra_allowances")


@app.route("/employee_login")
def employee_login():
    return render_template("employee_login.html")


@app.route("/employee_login1", methods=['post'])
def employee_login1():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email" : email, "password" : password}
    count = employee_collection.count_documents(query)
    if count > 0:
        employee = employee_collection.find_one(query)
        session["employee_id"] = str(employee["_id"])
        session['role'] = 'employee'
        session['wage_type'] = employee["wage_type"]
        day = datetime.now().strftime("%Y-%m-%d")
        query = {"day": day, "employee_id": employee["_id"]}
        count = time_sheet_col.count_documents(query)
        if count == 0:
            check_in = datetime.now().strftime("%H:%M")
            query = {"employee_id": employee["_id"], "day": day, "check_in": str(check_in), "status": "Checked In"}
            time_sheet_col.insert_one(query)
        return redirect("/employee_home")
    else:
        return render_template("mssg.html", message="Invalid Login")


@app.route("/employee_home")
def employee_home():
    query = {"_id": ObjectId(session['employee_id'])}
    employee = employee_collection.find_one(query)
    current_date = datetime.now().strftime("%Y-%m-%d")
    return render_template("employee_home.html", employee=employee, get_timesheet=get_timesheet, current_date=current_date, get_update_checkout=get_update_checkout)


def get_update_checkout(day):
    print(day)
    current_date = datetime.now().strftime("%Y-%m-%d")
    print(current_date != day)
    if current_date != day:
        query = {"day": day, "employee_id": ObjectId(session['employee_id'])}
        timesheet = time_sheet_col.find_one(query)
        time_sheet_id = timesheet['_id']
        check_in = datetime.now().strftime("%H:%M")

        query = {"_id": ObjectId(time_sheet_id)}
        query2 = {"$set": {"check_out": str(check_in)}}
        checkin_time = time_sheet_col.update_one(query, query2)
        return checkin_time


def get_timesheet(employee_id):
    query = {"employee_id": ObjectId(employee_id), "status": "Checked In"}
    timesheet = time_sheet_col.find_one(query)
    return timesheet


@app.route("/change_password")
def change_password():
    return render_template("change_password.html")


@app.route("/update_password")
def update_password():
    employee_id = session['employee_id']
    confirm_new_password = request.args.get("confirm_new_password")
    current_password = request.args.get("current_password")
    query = {"_id": ObjectId(employee_id), "password": current_password}
    count = employee_collection.count_documents(query)
    if count == 0:
        return render_template("mssg.html", message="password doesnot changed")
    else:
        query = {"_id": ObjectId(employee_id)}
        query2 = {"$set": {"password": confirm_new_password}}
        employee_collection.update_one(query, query2)
        return render_template("mssg.html", message="password changed successfully")


@app.route("/time_sheet")
def time_sheet():
    query = {}
    employee_id = request.args.get("employee_id")
    if session['role'] == 'employee':
        employee_id = session['employee_id']
        query = {"employee_id": ObjectId(employee_id)}
    elif session['role'] == 'admin':
        query = {"employee_id": ObjectId(employee_id)}
    time_sheets = time_sheet_col.find(query)
    current_date = datetime.now().strftime("%Y-%m-%d")
    return render_template("time_sheet.html", time_sheets=time_sheets, get_employee_id=get_employee_id, current_date=current_date)


@app.route("/check_out")
def check_out():
    time_sheet_id = request.args.get('time_sheet_id')
    query = {"_id": ObjectId(time_sheet_id)}
    time_sheet = time_sheet_col.find_one(query)

    day = time_sheet['day']+" "+time_sheet['check_in']
    day = datetime.strptime(day, "%Y-%m-%d %H:%M")
    date = datetime.now()
    diff = date - day
    rounded_hours = diff.total_seconds() / 3600
    check_out = datetime.now().strftime("%H:%M")
    query = {"_id": ObjectId(time_sheet_id)}
    query2 = {"$set": {"rounded_hours": round(rounded_hours, 2), "check_out": str(check_out), "status": "Checked Out"}}
    time_sheet_col.update_one(query, query2)

    # current_date = datetime.now().strftime("%Y-%m-%d")
    # day = time_sheet['day']
    # if current_date != day and time_sheet['status'] == "Checked In":
    #     check_in = datetime.now().strftime("%H:%M")
    #     query = {"_id": ObjectId(time_sheet_id)}
    #     query2 = {"$set": {"check_out": str(check_in), "status": "Checked Out"}}
    #     time_sheet_col.update_one(query, query2)
    return redirect("/time_sheet")
    # return render_template("mssg.html", message="Checked Out")


@app.route("/add_time_sheet")
def add_time_sheet():
    return render_template("add_time_sheet.html")


@app.route("/add_time_sheet1", methods=['post'])
def add_time_sheet1():
    employee_id = session['employee_id']
    day = request.form.get("day")
    check_in = request.form.get("check_in")
    check_out = request.form.get("check_out")
    check_in_time = day + ' ' + check_in
    check_in_time = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M")
    check_out_time = day + ' ' + check_out
    check_out_time = datetime.strptime(check_out_time, "%Y-%m-%d %H:%M")
    diff = check_out_time - check_in_time
    rounded_hours = diff.total_seconds() / 3600
    query = {"employee_id": ObjectId(employee_id), "day": day, "check_in": check_in, "check_out": check_out, "rounded_hours": rounded_hours}
    time_sheet_col.insert_one(query)
    return redirect("/time_sheet")


def get_employee_id(employee_id):
    query = {"_id": ObjectId(employee_id)}
    employee = employee_collection.find_one(query)
    return employee


@app.route("/apply_leave")
def apply_leave():
    query = {}
    employee_id = request.args.get("employee_id")
    if session['role'] == 'employee':
        employee_id = session['employee_id']
        query = {"employee_id": ObjectId(employee_id)}
    elif session['role'] == 'admin':
        query = {"employee_id": ObjectId(employee_id)}
    leaves = leaves_col.find(query)
    return render_template("apply_leave.html", leaves=leaves, get_employee_id=get_employee_id, get_deduction_id=get_deduction_id)


@app.route("/reason_for_apply")
def reason_for_apply():
    return render_template("reason_for_apply.html")


@app.route("/apply_leave1", methods=['post'])
def apply_leave1():
    employee_id = session['employee_id']
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    start_date = start_date.replace("T", " ")
    end_date = end_date.replace("T", " ")
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    delta = end_date - start_date
    no_of_days = delta.days
    print(no_of_days)
    reason = request.form.get("reason")
    status = "Applied For Leave"
    query = {"employee_id": ObjectId(employee_id), "start_date": start_date, "end_date": end_date, "no_of_days": no_of_days, "reason": reason ,"status": status}
    leaves_col.insert_one(query)
    return redirect("/apply_leave")


@app.route("/accept_leave")
def accept_leave():
    taxs = tax_collection.find()
    employee_id = request.args.get("employee_id")
    leave_id = request.args.get("leave_id")
    return render_template("deduction.html", taxs=taxs, employee_id=employee_id, leave_id=leave_id)


@app.route("/reject_leave")
def reject_leave():
    employee_id = request.args.get("employee_id")
    leave_id = request.args.get("leave_id")
    query = {"_id": ObjectId(leave_id)}
    query2 = {"$set": {"status": "Leave Rejected"}}
    leaves_col.update_one(query, query2)
    return redirect("/apply_leave?employee_id="+str(employee_id))


@app.route("/view_pay_salary")
def view_pay_salary():
    query = {}
    employee_id = request.args.get("employee_id")
    employee_type = request.args.get("employee_type")
    if session['role'] == 'employee':
        employee_id = session['employee_id']
        query = {"employee_id": ObjectId(employee_id)}
    elif session['role'] == 'admin':
        query = {"employee_id": ObjectId(employee_id)}
    pay_salaries = payrol_col.find(query)
    return render_template("view_pay_salary.html", pay_salaries=pay_salaries, employee_type=employee_type)


@app.route("/deduction")
def deduction():
    employee_id = request.args.get("employee_id")
    leave_id = request.args.get("leave_id")
    taxs = tax_collection.find()
    return render_template("deduction.html", employee_id=employee_id, leave_id=leave_id, taxs=taxs)


@app.route("/deduction1", methods=['post'])
def deduction1():
    employee_id = request.form.get("employee_id")
    deduction_type = request.form.get("deduction_type")
    query = {"_id": ObjectId(employee_id)}
    employee = employee_collection.find_one(query)
    wage_type = employee['wage_type']
    query = {"employee_id": ObjectId(employee_id)}
    pay_salary = payrol_col.find_one(query)

    tax_id = request.form.get("tax_id")
    query = {"_id": ObjectId(tax_id)}
    tax = tax_collection.find_one(query)
    tax = tax['tax_amount']
    leave_id = request.form.get("leave_id")
    query = {"_id": ObjectId(leave_id)}
    leave = leaves_col.find_one(query)
    no_of_days = leave['no_of_days']

    salary = pay_salary['income']
    per_day_salary = int(salary) / int(30)
    tax_amount = int(salary) * int(tax)/100
    leave_amount = int(per_day_salary) * int(no_of_days)
    deduction_amount = int(leave_amount) + int(tax_amount)
    query = {"employee_id": ObjectId(employee_id), "tax_id": ObjectId(tax_id), "leave_id": ObjectId(leave_id),
                 "deduction_amount": deduction_amount, "deduction_type": deduction_type}
    deduction_col.insert_one(query)

    query = {"_id": ObjectId(leave_id)}
    query2 = {"$set": {"status": "Leave Accepted"}}
    leaves_col.update_one(query, query2)
    return render_template("mssg.html", message="Employee Salary Deducted")


def get_deduction_id(leave_id, employee_id):
    query = {"employee_id": ObjectId(employee_id), "leave_id": ObjectId(leave_id)}
    count = deduction_col.count_documents(query)
    if count == 0:
        return True
    else:
        return False


@app.route("/view_deduction")
def view_deduction():
    employee_id = request.args.get("employee_id")
    leave_id = request.args.get("leave_id")
    query = {"_id": ObjectId(leave_id)}
    leave = leaves_col.find_one(query)
    no_of_days = leave['no_of_days']
    query = {"employee_id": ObjectId(employee_id), "leave_id": ObjectId(leave_id)}
    deduction = deduction_col.find_one(query)
    return render_template("view_deduction.html", no_of_days=no_of_days, deduction=deduction, get_employee_id=get_employee_id)


@app.route("/salary_report")
def salary_report():
    employee_id = request.args.get("employee_id")
    print(employee_id)
    time_sheet_id = request.args.get("time_sheet_id")
    query = {"employee_id": ObjectId(employee_id)}
    print(query)
    reports = salary_report_col.find(query)
    return render_template("salary_report.html", reports=reports,get_extra_allowances=get_extra_allowances, get_deduction_id_by_salary=get_deduction_id_by_salary, employee_id=employee_id, time_sheet_id=time_sheet_id, get_employee_id=get_employee_id)


@app.route("/add_salary_report")
def add_salary_report():
    employee_id = request.args.get("employee_id")
    time_sheet_id = request.args.get("time_sheet_id")
    allowances = extra_allowances_col.find()
    return render_template("add_salary_report.html", employee_id=employee_id, time_sheet_id=time_sheet_id, allowances=allowances)


@app.route("/add_salary_report1", methods=['post'])
def add_salary_report1():
    employee_id = request.form.get("employee_id")
    query = {"_id": ObjectId(employee_id)}
    employee = employee_collection.find_one(query)

    allowance_id = request.form.get("allowance_id")
    query = {"_id": ObjectId(allowance_id)}
    allowance = extra_allowances_col.find_one(query)
    bonus = allowance['bonus']
    insurance = allowance['insurance']

    query = {"employee_id": ObjectId(employee_id)}
    pay_salary = payrol_col.find_one(query)
    payroll_id = pay_salary['_id']

    query = {"employee_id": ObjectId(employee_id)}
    deduction = deduction_col.find_one(query)

    if employee['wage_type'] == "hour_based":
        time_sheet_id = request.form.get("time_sheet_id")
        query = {"_id": ObjectId(time_sheet_id)}
        time_sheet = time_sheet_col.find_one(query)
        hours_worked = time_sheet['rounded_hours']

        hourly_wage = pay_salary['hourly_wage']
        total_salary = int(hours_worked) * int(hourly_wage)
        query = {"employee_id": ObjectId(employee_id), "time_sheet_id": ObjectId(time_sheet_id), "allowance_id": ObjectId(allowance_id), "total_salary": total_salary, "hours_worked": hours_worked, "payroll_id": ObjectId(payroll_id)}
    elif employee['wage_type'] == "salary_based":
        salary = pay_salary['income']
        deduction_id = deduction['_id']
        deduction_amount = deduction['deduction_amount']
        salary = int(salary) + int(bonus) + int(insurance)
        total_salary = int(salary) - int(deduction_amount)
        over_time = request.form.get("over_time")
        query = {"employee_id": ObjectId(employee_id), "allowance_id": ObjectId(allowance_id), "deduction_id": ObjectId(deduction_id), "total_salary": total_salary, "payroll_id": ObjectId(payroll_id), "over_time": over_time}
    salary_report_col.insert_one(query)
    return redirect("/salary_report")


def get_deduction_id_by_salary(deduction_id):
    query = {"_id": ObjectId(deduction_id)}
    deduction = deduction_col.find_one(query)
    deduction_amount = deduction['deduction_amount']
    return deduction_amount


def get_extra_allowances(allowance_id):
    query = {"_id": ObjectId(allowance_id)}
    allowance = extra_allowances_col.find_one(query)
    return allowance


def get_pay_salary(employee_id):
    query = {"employee_id": ObjectId(employee_id)}
    payrol = payrol_col.find_one(query)
    return payrol


app.run(debug=True)