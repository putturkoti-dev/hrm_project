from django.contrib import admin
from .models import Company, Department, Employee, Attendance, LeaveRequest, Payroll, Holiday


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "user", "department", "job_title")
    search_fields = ("employee_id", "user__username", "user__first_name", "user__last_name")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "check_in", "check_out")
    list_filter = ("date", "employee__department")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "start_date", "end_date", "status")
    list_filter = ("status",)


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ("employee", "month", "net_salary", "generated_at")
    list_filter = ("month",)


admin.site.register(Holiday)