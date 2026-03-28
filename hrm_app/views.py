import datetime
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse

from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .models import EmployeeDocument
from .forms import EmployeeDocumentForm
from .forms import ReportingManagerForm
from .models import Holiday, LeaveBalance

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Employee, Department, Attendance, LeaveRequest, Payroll, Company
from .forms import (
    EmployeeForm,
    EmployeeBankForm,
    EmployeeIdentityForm,
    EmployeePhotoForm,
    EmployeePersonalForm,
    EmployeeJobForm,
    EmployeeContactForm,
    UserForm,
    DepartmentForm,
    LeaveRequestForm,
    CompanySignupForm,
    EmployeeContactForm,
    EmployeeJobForm
)

from .decorators import hr_required
from django.http import HttpResponseForbidden


# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------

def get_employee(request):
    employee = Employee.objects.filter(user=request.user).first()
    if not employee:
        return None
    return employee


# ---------------------------------------------------
# AUTH / HOME
# ---------------------------------------------------

def home(request):
    return redirect("hrm:dashboard")


def logout_get(request):
    logout(request)
    return redirect("login")


# ---------------------------------------------------
# COMPANY SIGNUP
# ---------------------------------------------------

def company_signup(request):
    if request.user.is_authenticated:
        return redirect("hrm:dashboard")

    if request.method == "POST":
        form = CompanySignupForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data["company_name"]
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return redirect("hrm:company_signup")

            company, _ = Company.objects.get_or_create(name=company_name)

            user = User.objects.create_user(
                username=username,
                password=password
            )

            Employee.objects.create(
                user=user,
                company=company,
                employee_id=f"HR-{uuid.uuid4().hex[:6]}",
                role="HR"
            )

            login(request, user)
            return redirect("hrm:dashboard")
    else:
        form = CompanySignupForm()

    return render(request, "hrm_app/company_signup.html", {"form": form})


# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------
import calendar
@login_required
def dashboard(request):
    employee = request.user.employee_profile
    company = employee.company

    total_employees = Employee.objects.filter(company=company).count()

    today = datetime.date.today()
    today_attendance = Attendance.objects.filter(
        employee__company=company,
        date=today
    ).count()

    pending_leaves = LeaveRequest.objects.filter(
        company=company,
        status="P"
    ).count()

    total_payroll = Payroll.objects.filter(company=company)\
        .aggregate(total=Sum("net_salary"))["total"] or 0

    from django.utils import timezone

    today = timezone.localdate()

    # Present (unique employees for today)
    present = Attendance.objects.filter(
        employee__company=company,
        date=today,
        check_in__isnull=False
    ).values('employee').distinct().count()

    # Absent (correct calculation)
    absent = total_employees - present

    leaves = LeaveRequest.objects.filter(
        company=company,
        status="A"
    ).count()
    current_year = datetime.date.today().year

    monthly_attendance = []

    for month in range(1, 13):
        count = Attendance.objects.filter(
            employee__company=company,
            date__year=current_year,
            date__month=month,
            check_in__isnull=False
        ).count()

        monthly_attendance.append(count)

    upcoming_holidays = Holiday.objects.filter(
        date__gte=datetime.date.today()
    ).order_by("date")[:5]

    employee_growth = []

    for month in range(1, 13):
        count = Employee.objects.filter(
            company=company,
            date_joined__year=current_year,
            date_joined__month=month
        ).count()

        employee_growth.append(count)

    late_checkins = Attendance.objects.filter(
        employee__company=company,
        date=today,
        check_in__gt=datetime.time(9, 30)
    ).count()

    leave_balances = LeaveBalance.objects.filter(employee=employee)


    return render(request, "hrm_app/dashboard.html", {
        "total_employees": total_employees,
        "today_attendance": today_attendance,
        "pending_leaves": pending_leaves,
        "total_payroll": total_payroll,
        "present": present,
        "absent": absent,
        "leaves": leaves,
        "monthly_attendance": monthly_attendance,
        "upcoming_holidays": upcoming_holidays,
        "employee_growth": employee_growth,
        "late_checkins": late_checkins,
        "leave_balances": leave_balances,
    })
# ---------------------------------------------------
# DEPARTMENTS
# ---------------------------------------------------
@login_required
@hr_required
def department_create(request):
    employee = request.user.employee_profile
    company = employee.company

    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save(commit=False)
            dept.company = company   # 🔒 lock to company
            dept.save()
            messages.success(request, "Department created successfully")
            return redirect("hrm:department_list")
    else:
        form = DepartmentForm()

    return render(request, "hrm_app/department_form.html", {"form": form})


# ---------------------------------------------------
# EMPLOYEES
# ---------------------------------------------------

@login_required
@hr_required
def department_list(request):
    company = request.user.employee_profile.company
    departments = Department.objects.filter(company=company)
    return render(request, "hrm_app/department_list.html", {"departments": departments})


from .models import LeaveBalance
@login_required
@hr_required
def employee_create(request):
    company = request.user.employee_profile.company

    if request.method == "POST":
        user_form = UserForm(request.POST)
        employee_form = EmployeeForm(request.POST, company=company)

        if user_form.is_valid() and employee_form.is_valid():
            # Save user
            user = user_form.save(commit=False)
            user.set_password("123456")  # temporary password
            user.save()

            # Save employee
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.company = company
            employee.save()


            LeaveBalance.objects.create(employee=employee, leave_type="CL", total_days=12)
            LeaveBalance.objects.create(employee=employee, leave_type="SL", total_days=8)
            LeaveBalance.objects.create(employee=employee, leave_type="EL", total_days=15)

            messages.success(request, "Employee created successfully")
            return redirect("hrm:employee_list")
        else:
            print(user_form.errors)
            print(employee_form.errors)

    else:
        user_form = UserForm()
        employee_form = EmployeeForm(company=company)

    return render(request, "hrm_app/employee_form.html", {
        "user_form": user_form,
        "employee_form": employee_form
    })

@login_required
@hr_required
def employee_list(request):
    company = request.user.employee_profile.company

    employees = Employee.objects.filter(company=company)

    # 🔍 SEARCH
    search = request.GET.get("search")
    if search:
        employees = employees.filter(
            user__first_name__icontains=search
        ) | employees.filter(
            employee_id__icontains=search
        )

    # 📂 DEPARTMENT FILTER
    department = request.GET.get("department")
    if department:
        employees = employees.filter(department_id=department)

    # 👤 ROLE FILTER
    role = request.GET.get("role")
    if role:
        employees = employees.filter(role=role)

    departments = Department.objects.filter(company=company)

    return render(request, "hrm_app/employee_list.html", {
        "employees": employees,
        "departments": departments,
    })
@hr_required
def employee_edit(request, pk):
    hr = get_employee(request)
    if not hr:
        return redirect("hrm:company_signup")

    employee = get_object_or_404(
        Employee,
        pk=pk,
        company=hr.company
    )

    user = employee.user

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        employee_form = EmployeeForm(request.POST, instance=employee)

        if user_form.is_valid() and employee_form.is_valid():
            user_form.save()
            employee_form.save()
            messages.success(request, "Employee updated")
            return redirect("hrm:employee_list")
    else:
        user_form = UserForm(instance=user)
        employee_form = EmployeeForm(instance=employee)

    return render(
        request,
        "hrm_app/employee_form.html",
        {
            "user_form": user_form,
            "form": employee_form,
            "title": "Edit Employee"
        },
    )


@hr_required
def employee_delete(request, pk):
    emp = get_object_or_404(
        Employee,
        pk=pk,
        company=request.user.employee_profile.company
    )
    if request.method == "POST":
        emp.user.delete()
        emp.delete()
        return redirect("hrm:employee_list")

    return render(request, "hrm_app/employee_confirm_delete.html", {"employee": emp})


# ---------------------------------------------------
# LEAVES
# ---------------------------------------------------

@login_required
def leave_list(request):
    employee = request.user.employee_profile

    if employee.role == "HR":
        leaves = LeaveRequest.objects.filter(company=employee.company)
    else:
        leaves = LeaveRequest.objects.filter(employee=employee)

    return render(request, "hrm_app/leave_list.html", {"leaves": leaves})

@login_required
def leave_apply(request):
    employee = get_employee(request)
    if not employee:
        return redirect("hrm:company_signup")

    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.company = employee.company
            leave.save()
            messages.success(request, "Leave applied")
            return redirect("hrm:leave_list")
    else:
        form = LeaveRequestForm()

    return render(request, "hrm_app/leave_form.html", {"form": form})


from .decorators import hr_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect


@login_required
@hr_required
def leave_approve(request, pk):
    employee = request.user.employee_profile
    leave = get_object_or_404(
        LeaveRequest,
        pk=pk,
        company=employee.company
    )
    if leave.status != "A":
        leave.status = "A"

        leave_days = (leave.end_date - leave.start_date).days + 1

        balance = LeaveBalance.objects.filter(
            employee=leave.employee,
            leave_type=leave.leave_type
        ).first()

        if balance:
            balance.used_days += leave_days
            balance.save()

        leave.save()
    return redirect("hrm:leave_list")


@login_required
@hr_required
def leave_reject(request, pk):
    employee = request.user.employee_profile
    leave = get_object_or_404(
        LeaveRequest,
        pk=pk,
        company=employee.company
    )
    leave.status = "R"
    leave.save()
    return redirect("hrm:leave_list")


@login_required
def leave_pending(request):
    employee = get_employee(request)
    if not employee:
        return redirect("hrm:company_signup")

    leaves = LeaveRequest.objects.filter(
        company=employee.company,
        status="P"
    ).order_by("-applied_at")

    return render(
        request,
        "hrm_app/leave_list.html",
        {"leaves": leaves}
    )


# ---------------------------------------------------
# ATTENDANCE
# ---------------------------------------------------

@login_required
def attendance_today(request):
    employee = get_employee(request)
    if not employee:
        return redirect("hrm:company_signup")

    today = datetime.date.today()
    attendance, _ = Attendance.objects.get_or_create(
        employee=employee,
        date=today
    )

    return render(request, "hrm_app/attendance_today.html", {
        "attendance": attendance,
        "today": today
    })


@login_required
def clock_in(request):
    employee = get_employee(request)
    if not employee:
        return redirect("hrm:company_signup")

    today = datetime.date.today()
    attendance, _ = Attendance.objects.get_or_create(
        employee=employee,
        date=today
    )

    if not attendance.check_in:
        attendance.check_in = timezone.localtime().time()
        attendance.save()
        messages.success(request, "Clocked in")

    return redirect("hrm:attendance_today")


@login_required
def clock_out(request):
    employee = get_employee(request)
    if not employee:
        return redirect("hrm:company_signup")

    today = datetime.date.today()
    attendance = Attendance.objects.filter(
        employee=employee,
        date=today
    ).first()

    if attendance and not attendance.check_out:
        attendance.check_out = timezone.localtime().time()
        attendance.save()
        messages.success(request, "Clocked out")

    return redirect("hrm:attendance_today")


@login_required
def attendance_history(request):
    employee = get_employee(request)
    if not employee:
        return redirect("hrm:company_signup")

    records = Attendance.objects.filter(employee=employee).order_by("-date")
    return render(request, "hrm_app/attendance_history.html", {"records": records})


# ---------------------------------------------------
# PAYROLL
# ---------------------------------------------------

@hr_required
def payroll_list(request):
    employee = get_employee(request)
    if not employee:
        return redirect("hrm:company_signup")

    payrolls = Payroll.objects.filter(company=employee.company)
    return render(request, "hrm_app/payroll_list.html", {"payrolls": payrolls})


@hr_required
def generate_payslip(request, pk):
    employee = get_employee(request)
    if not employee:
        return redirect("hrm:company_signup")

    payroll = get_object_or_404(
        Payroll,
        pk=pk,
        company=employee.company
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Payslip_{payroll.employee.employee_id}.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    p.setFont("Helvetica", 11)

    p.drawString(50, 800, "Payslip")
    p.drawString(50, 770, f"Employee: {payroll.employee.user.get_full_name()}")
    p.drawString(50, 750, f"Employee ID: {payroll.employee.employee_id}")
    p.drawString(50, 730, f"Month: {payroll.month}")
    p.drawString(50, 700, f"Net Salary: ₹{payroll.net_salary}")

    p.showPage()
    p.save()

    return response


@login_required
def employee_profile(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if employee.company != request.user.employee_profile.company:
        return HttpResponseForbidden("Not allowed")

    # ✅ THIS IS THE FIX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "hrm_app/employee_profile_partial.html", {
            "employee": employee
        })

    return render(request, "hrm_app/employee_profile.html", {
        "employee": employee
    })
# ---------------------------------------------------
# EMPLOYEE SELF PROFILE (STEP 2.1)
# ---------------------------------------------------

@login_required
def employee_self_profile(request):
    employee = request.user.employee_profile

    return render(
        request,
        "hrm_app/employee_profile.html",
        {
            "employee": employee,
            "self_view": True,   # 🔥 IMPORTANT FLAG
        }
    )

@login_required
def employee_personal(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    # Security: only same company
    if employee.company != request.user.employee_profile.company:
        return redirect("hrm:employee_list")

    if request.method == "POST":
        form = EmployeePersonalForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Personal details updated successfully")
            return redirect("hrm:employee_personal", pk=pk)
    else:
        form = EmployeePersonalForm(instance=employee)

    return render(request, "hrm_app/employee_personal.html", {
        "employee": employee,
        "form": form
    })


@login_required
@hr_required
def employee_job_edit(request, pk):

    employee = get_object_or_404(Employee, pk=pk)

    if employee.company != request.user.employee_profile.company:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        form = EmployeeJobForm(request.POST, instance=employee)

        if form.is_valid():
            form.save()

            # ✅ AJAX RESPONSE
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return render(request, "hrm_app/employee_profile_partial.html", {
                    "employee": employee
                })

            messages.success(request, "Job details updated successfully")
            return redirect("hrm:employee_profile", pk=pk)

    else:
        form = EmployeeJobForm(instance=employee)

    # ✅ IMPORTANT (FOR EDIT CLICK)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "hrm_app/employee_job_form.html", {
            "employee": employee,
            "form": form,
        })

    return render(
        request,
        "hrm_app/employee_job_form.html",
        {
            "employee": employee,
            "form": form,
        },
    )

@login_required
@hr_required
def employee_contact_edit(request, pk):
    # ✅ REQUIRED: define employee FIRST
    employee = get_object_or_404(Employee, pk=pk)

    # ✅ Company isolation (same pattern as your other views)
    if employee.company != request.user.employee_profile.company:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        form = EmployeeContactForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Contact details updated successfully")
            return redirect("hrm:employee_profile", pk=pk)
    else:
        form = EmployeeContactForm(instance=employee)

    return render(
        request,
        "hrm_app/employee_contact_form.html",
        {
            "employee": employee,
            "form": form,
        },
    )

@login_required
def employee_photo_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    # 🔒 Company isolation
    if employee.company != request.user.employee_profile.company:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        form = EmployeePhotoForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile photo updated successfully")
            return redirect("hrm:employee_profile", pk=pk)
    else:
        form = EmployeePhotoForm(instance=employee)

    return render(
        request,
        "hrm_app/employee_photo_form.html",
        {
            "employee": employee,
            "form": form,
        }
    )


@login_required
def employee_documents(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    # 🔒 Company isolation
    if employee.company != request.user.employee_profile.company:
        return HttpResponseForbidden("Not allowed")

    # 🔒 Employee can access only own documents
    if request.user.employee_profile.role == "EMP" and request.user.employee_profile != employee:
        return HttpResponseForbidden("Not allowed")

    documents = employee.documents.all()

    if request.method == "POST":
        form = EmployeeDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.employee = employee
            doc.save()
            messages.success(request, "Document uploaded")
            return redirect("hrm:employee_documents", pk=pk)
    else:
        form = EmployeeDocumentForm()

    return render(
        request,
        "hrm_app/employee_documents.html",
        {
            "employee": employee,
            "documents": documents,
            "form": form,
        }
    )
@login_required
def delete_employee_document(request, doc_id):
    document = get_object_or_404(EmployeeDocument, id=doc_id)
    employee = document.employee

    if employee.company != request.user.employee_profile.company:
        return HttpResponseForbidden("Not allowed")

    if request.user.employee_profile.role == "EMP" and request.user.employee_profile != employee:
        return HttpResponseForbidden("Not allowed")

    document.delete()
    messages.success(request, "Document deleted")
    return redirect("hrm:employee_documents", pk=employee.id)
@login_required
@hr_required
def employee_reporting_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    # 🔒 Company isolation
    if employee.company != request.user.employee_profile.company:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        form = ReportingManagerForm(
            request.POST,
            instance=employee,
            company=request.user.employee_profile.company
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Reporting manager updated successfully")
            return redirect("hrm:employee_profile", pk=pk)
    else:
        form = ReportingManagerForm(
            instance=employee,
            company=request.user.employee_profile.company
        )

    return render(
        request,
        "hrm_app/employee_reporting_edit.html",
        {
            "employee": employee,
            "form": form,
        }
    )
@login_required
@hr_required
def employee_bank_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    form = EmployeeBankForm(
        request.POST or None,
        instance=employee
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Bank details updated")
        return redirect("hrm:employee_profile", pk=employee.pk)

    return render(request, "hrm_app/employee_bank_edit.html", {
        "employee": employee,
        "form": form
    })
@login_required
@hr_required
def employee_identity_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    form = EmployeeIdentityForm(
        request.POST or None,
        instance=employee
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Identity details updated")
        return redirect("hrm:employee_profile", pk=employee.pk)

    return render(request, "hrm_app/employee_identity_edit.html", {
        "employee": employee,
        "form": form
    })

import calendar
from datetime import date, timedelta
from django.utils import timezone
today = date.today()
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Attendance, LeaveRequest ,Holiday, Employee
from .models import LeaveBalance   # make sure this is imported

@login_required
def attendance_calendar(request):

    today = date.today()

    month = int(request.GET.get("month", today.month))
    year = int(request.GET.get("year", today.year))
    month_name = calendar.month_name[month]
    # create current date
    current_date = date(year, month, 1)

    # next month
    next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    # previous month
    prev_month = (current_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    cal = calendar.monthcalendar(year, month)

    employee = Employee.objects.filter(user=request.user).first()

    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year
    )

    leave_records = LeaveRequest.objects.filter(
        employee=employee,
        status="A"
    )

    holiday_records = Holiday.objects.filter(
        date__year=year,
        date__month=month
    )

    # ✅ ADD THIS (Leave Balance Query)
    leave_balances = LeaveBalance.objects.filter(employee=employee)

    attendance_dict = {}

    # Step 1: mark all present days
    present_days = set()

    for record in attendance_records:
        if record.check_in:
            attendance_dict[record.date.day] = "Present"
            present_days.add(record.date.day)

    # Step 2: mark leave
    for leave in leave_records:
        current = leave.start_date
        while current <= leave.end_date:
            if current.month == month and current.year == year:
                attendance_dict[current.day] = "Leave"
            current += timedelta(days=1)

    # Step 3: mark holidays
    holiday_days = set()
    for holiday in holiday_records:
        holiday_days.add(holiday.date.day)
        attendance_dict[holiday.date.day] = "Holiday"

    # Step 4: mark absents (IMPORTANT FIX 🔥)
    for week in cal:
        for day in week:
            if day != 0:

                current_date = datetime.date(year, month, day)
                weekday = current_date.weekday()  # Monday=0 ... Sunday=6

                # ✅ Sunday = Holiday
                if weekday == 6:
                    attendance_dict[day] = "Holiday"

                # ✅ If not already marked
                elif day not in attendance_dict:
                    if current_date <= today:
                        attendance_dict[day] = "Absent"

    context = {
        "calendar": cal,
        "attendance": attendance_dict,
        "month": month,
        "year": year,
        "today": today,
        "leave_balances": leave_balances,
        "next_month": next_month,
        "prev_month": prev_month,
        "month_name": month_name,
    }

    return render(request, "hrm_app/attendance_calendar.html", context)
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date
from calendar import monthrange
from .models import Employee, Payroll, Attendance

from calendar import monthrange
@login_required
def generate_monthly_payroll(request):

    today = date.today()

    payroll_month = date(today.year, today.month, 1)

    company = request.user.employee_profile.company

    employees = Employee.objects.filter(company=company)

    created = 0

    for emp in employees:

        # avoid duplicate payroll
        if Payroll.objects.filter(employee=emp, month=payroll_month).exists():
            continue

        # count absent days
        total_days = monthrange(today.year, today.month)[1]

        present_days = Attendance.objects.filter(
            employee=emp,
            date__year=today.year,
            date__month=today.month,
            check_in__isnull=False
        ).count()

        absent_days = total_days - present_days

        Payroll.objects.create(
            company=emp.company,
            employee=emp,
            month=payroll_month,
            basic_salary=getattr(emp, "salary", 0) or 0,
            allowances=0,
            deductions=0,
            absent_days=absent_days
        )

        created += 1

    messages.success(
        request,
        f"{created} payroll records generated for {payroll_month.strftime('%B %Y')}"
    )

    return redirect("hrm:payroll_list")

from calendar import monthrange
from datetime import date
from .models import Attendance, Payroll

def calculate_absent_days(employee, year, month):
    total_days = monthrange(year, month)[1]

    present_days = Attendance.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month
    ).count()

    return total_days - present_days
@login_required
def generate_payroll_range(request):

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if not from_date or not to_date:
        messages.error(request, "Please select dates")
        return redirect("hrm:payroll_list")

    from datetime import datetime

    from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
    to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

    company = request.user.employee_profile.company

    employees = Employee.objects.filter(company=company)

    total_days = (to_date - from_date).days + 1

    created = 0

    for emp in employees:

        attendances = Attendance.objects.filter(
            employee=emp,
            date__range=[from_date, to_date],
            check_in__isnull=False
        )

        present_days = attendances.count()

        absent_days = total_days - present_days

        basic_salary = getattr(emp, "salary", 0) or 0

        per_day_salary = basic_salary / total_days if total_days else 0

        absence_deduction = absent_days * per_day_salary

        Payroll.objects.create(
            company=emp.company,
            employee=emp,
            month=from_date,
            basic_salary=basic_salary,
            allowances=0,
            deductions=0,
            absent_days=absent_days,
            absence_deduction=absence_deduction
        )

        created += 1

    messages.success(request, f"{created} payroll records generated.")

    return redirect("hrm:payroll_list")