from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "hrm"

urlpatterns = [

    # Home
    path("", views.home, name="home"),

    # ================= AUTH =================
    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="hrm_app/password_change.html",
            success_url="/password-change-done/"
        ),
        name="password_change",
    ),

    path(
        "password-change-done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="hrm_app/password_change_done.html"
        ),
        name="password_change_done",
    ),

    path("accounts/logout/", views.logout_get, name="logout"),

    # ================= DEPARTMENTS =================
    path("departments/", views.department_list, name="department_list"),
    path("departments/create/", views.department_create, name="department_create"),

    # ================= EMPLOYEES =================
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/create/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/edit/", views.employee_edit, name="employee_edit"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),

    # ================= LEAVES =================
    path("leaves/", views.leave_list, name="leave_list"),
    path("leaves/apply/", views.leave_apply, name="leave_apply"),
    path("leaves/pending/", views.leave_pending, name="leave_pending"),
    path("leaves/approve/<int:pk>/", views.leave_approve, name="leave_approve"),
    path("leaves/reject/<int:pk>/", views.leave_reject, name="leave_reject"),

    # ================= ATTENDANCE =================
    path("attendance/today/", views.attendance_today, name="attendance_today"),
    path("attendance/clock-in/", views.clock_in, name="clock_in"),
    path("attendance/clock-out/", views.clock_out, name="clock_out"),
    path("attendance/history/", views.attendance_history, name="attendance_history"),

    # ================= PAYROLL =================
    path("payroll/", views.payroll_list, name="payroll_list"),
    path("payroll/payslip/<int:pk>/", views.generate_payslip, name="generate_payslip"),

    # ================= DASHBOARD =================
    path("dashboard/", views.dashboard, name="dashboard"),

    # ================= SIGNUP =================
    path("signup/", views.company_signup, name="company_signup"),

    # ================= Employee profile =================
    path("employees/<int:pk>/", views.employee_profile, name="employee_profile"),
    path("employees/<int:pk>/personal/", views.employee_personal, name="employee_personal"),
    path("employees/<int:pk>/job/edit/",views.employee_job_edit,name="employee_job_edit"),
    path("employees/<int:pk>/contact/edit/",views.employee_contact_edit,name="employee_contact_edit"),
    path("employees/<int:pk>/photo/edit/", views.employee_photo_edit, name="employee_photo_edit"),
    path("employees/<int:pk>/documents/",views.employee_documents,name="employee_documents"),
    path("documents/<int:doc_id>/delete/",views.delete_employee_document,name="delete_employee_document"),
    path("employees/<int:pk>/reporting/edit/",views.employee_reporting_edit,name="employee_reporting_edit"),
    path("my-profile/", views.employee_self_profile, name="employee_self_profile"),
    path("employees/<int:pk>/edit/bank/", views.employee_bank_edit, name="employee_bank_edit"),
    path("employees/<int:pk>/edit/identity/", views.employee_identity_edit, name="employee_identity_edit"),
    # ================= Employee profile =================
    path('attendance/calendar/', views.attendance_calendar, name='attendance_calendar'),
path(
    "payroll/generate/",
    views.generate_monthly_payroll,
    name="generate_monthly_payroll"
),
    path("payroll/", views.payroll_list, name="payroll_list"),

    path(
        "payroll/generate-range/",
        views.generate_payroll_range,
        name="generate_payroll_range",
    ),
]
