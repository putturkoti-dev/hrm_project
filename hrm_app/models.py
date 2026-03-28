from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Department(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="departments"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)  # 👈 IMPORTANT

    def __str__(self):
        return f"{self.name} ({self.company.name})"



GENDER_CHOICES = (
    ("M", "Male"),
    ("F", "Female"),
    ("O", "Other"),
)


ROLE_CHOICES = (
    ("ADMIN", "Admin"),
    ("HR", "HR"),
    ("EMP", "Employee"),
)

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Employee(models.Model):
    profile_photo = models.ImageField(upload_to="employee_photos/", blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    employee_id = models.CharField(max_length=20, unique=True)
    ROLE_CHOICES = (
        ("HR", "HR"),
        ("EMP", "Employee"),
    )
    role = models.CharField(max_length=3, choices=ROLE_CHOICES, default="EMP")
    reporting_manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates"
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    job_title = models.CharField(max_length=100, blank=True)

    # ---------------- PERSONAL ----------------
    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    )

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)

    # ---------------- CONTACT ----------------
    phone = models.CharField(max_length=20, blank=True)
    alternate_phone = models.CharField(max_length=20, blank=True)

    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True)

    # ---------------- JOB ----------------
    EMPLOYMENT_TYPE_CHOICES = (
        ("FT", "Full Time"),
        ("PT", "Part Time"),
        ("CT", "Contract"),
        ("IN", "Intern"),
    )

    employment_type = models.CharField(
        max_length=2,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default="FT"
    )

    work_location = models.CharField(max_length=100, blank=True)
    date_joined = models.DateField(default=timezone.now)
    # ---------------- PERSONAL EXTRA ----------------
    BLOOD_GROUP_CHOICES = (
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("O+", "O+"),
        ("O-", "O-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
    )

    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        blank=True
    )

    MARITAL_STATUS_CHOICES = (
        ("S", "Single"),
        ("M", "Married"),
        ("D", "Divorced"),
        ("W", "Widowed"),
    )

    marital_status = models.CharField(
        max_length=1,
        choices=MARITAL_STATUS_CHOICES,
        blank=True
    )

    # ---------------- PAYROLL ----------------
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=30, blank=True)
    ifsc_code = models.CharField(max_length=15, blank=True)

    # ---------------- IDENTITY ----------------
    aadhar_number = models.CharField(max_length=12, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)

    # ---------------- META ----------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

from datetime import time, datetime

class Attendance(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    date = models.DateField()

    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    # Smart attendance fields
    is_late = models.BooleanField(default=False)
    early_exit = models.BooleanField(default=False)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("employee", "date")
        ordering = ["-date"]

    def save(self, *args, **kwargs):

        office_start = time(9, 0)
        office_end = time(18, 0)

        # Late check-in
        if self.check_in and self.check_in > office_start:
            self.is_late = True
        else:
            self.is_late = False

        # Early exit
        if self.check_out and self.check_out < office_end:
            self.early_exit = True
        else:
            self.early_exit = False

        # Overtime calculation
        if self.check_out and self.check_out > office_end:
            overtime = datetime.combine(self.date, self.check_out) - datetime.combine(self.date, office_end)
            self.overtime_hours = overtime.seconds / 3600
        else:
            self.overtime_hours = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.date}"

LEAVE_STATUS = (
    ("P", "Pending"),
    ("A", "Approved"),
    ("R", "Rejected"),
)


class LeaveRequest(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    # ✅ ADD THIS
    LEAVE_TYPE_CHOICES = (
        ("CL", "Casual Leave"),
        ("SL", "Sick Leave"),
        ("EL", "Earned Leave"),
    )

    leave_type = models.CharField(
        max_length=2,
        choices=LEAVE_TYPE_CHOICES,
        default="CL"
    )

    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=1, choices=LEAVE_STATUS, default="P")
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} {self.start_date} -> {self.end_date} [{self.get_status_display()}]"



class Payroll(models.Model):

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    month = models.DateField()  # e.g. "2025-03"

    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)

    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # HR deduction fields
    absent_days = models.IntegerField(default=0)
    absence_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    net_salary = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    generated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        from calendar import monthrange

        # ensure values are not None
        basic = self.basic_salary or 0
        allowance = self.allowances or 0
        deduction = self.deductions or 0
        absent = self.absent_days or 0

        year = self.month.year
        month = self.month.month

        total_days = monthrange(year, month)[1]

        # salary per day
        per_day_salary = basic / total_days if total_days else 0

        # absence deduction
        self.absence_deduction = absent * per_day_salary

        total_deductions = deduction + self.absence_deduction

        # final salary
        self.net_salary = basic + allowance - total_deductions

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.month}"

class EmployeeDocument(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to="employee_documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.employee}"

class Holiday(models.Model):

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.date})"

class LeaveBalance(models.Model):

    LEAVE_TYPE_CHOICES = (
        ("CL", "Casual Leave"),
        ("SL", "Sick Leave"),
        ("EL", "Earned Leave"),
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_balances"
    )

    leave_type = models.CharField(
        max_length=2,
        choices=LEAVE_TYPE_CHOICES
    )

    total_days = models.IntegerField(default=12)
    used_days = models.IntegerField(default=0)

    def remaining_days(self):
        return self.total_days - self.used_days

    def __str__(self):
        return f"{self.employee} - {self.leave_type}"