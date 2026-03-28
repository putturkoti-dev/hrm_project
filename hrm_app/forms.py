from django import forms
from django.contrib.auth.models import User
from .models import Employee, Department, LeaveRequest, EmployeeDocument


# ---------------- DEPARTMENT ----------------
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "description"]


# ---------------- USER ----------------
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]


# ---------------- EMPLOYEE CREATE ----------------
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "department",
            "job_title",
            "employment_type",
            "reporting_manager",
            "work_location",
            "date_of_birth",
            "gender",
            "blood_group",
            "marital_status",
            "phone",
            "alternate_phone",
            "address",
            "city",
            "state",
            "pincode",
            "emergency_contact_name",
            "emergency_contact_number",
            "salary",
            "bank_name",
            "account_number",
            "ifsc_code",
            "aadhar_number",
            "pan_number",
            "date_joined",
        ]

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

        if company:
            self.fields["department"].queryset = Department.objects.filter(company=company)
        else:
            self.fields["department"].queryset = Department.objects.none()


# ---------------- PERSONAL TAB ----------------
class EmployeePersonalForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["gender", "date_of_birth","blood_group",
            "marital_status"]


# ---------------- JOB TAB ----------------
class EmployeeJobForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["department", "job_title", "role", "employment_type","work_location","date_joined"]

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        if company:
            self.fields["department"].queryset = Department.objects.filter(company=company)


# ---------------- CONTACT TAB ----------------
class EmployeeContactForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Employee
        fields = [
            "phone",
            "alternate_phone",
            "address",
            "city",
            "state",
            "pincode",


        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["email"].initial = self.instance.user.email

    def save(self, commit=True):
        employee = super().save(commit=False)
        employee.user.email = self.cleaned_data["email"]
        if commit:
            employee.user.save()
            employee.save()
        return employee

# ---------------- PHOTO ----------------
class EmployeePhotoForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["profile_photo"]


# ---------------- LEAVE ----------------
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }
class CompanySignupForm(forms.Form):
    company_name = forms.CharField(max_length=100)
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


# ---------------- DOCUMENTS ----------------
class EmployeeDocumentForm(forms.ModelForm):
    class Meta:
        model = EmployeeDocument
        fields = ["title", "file"]

# ---------------- EMPLOYEE REPORTING FORM ----------------
class ReportingManagerForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["reporting_manager"]

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

        if company:
            self.fields["reporting_manager"].queryset = (
                Employee.objects.filter(company=company)
            )

from django import forms
from .models import Employee
class EmployeeBankForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "bank_name",
            "account_number",
            "ifsc_code",
            "salary",
        ]
class EmployeeIdentityForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "aadhar_number",
            "pan_number",
        ]
