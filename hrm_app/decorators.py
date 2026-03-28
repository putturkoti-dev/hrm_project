from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib import messages


def hr_required(view_func):
    def wrapper(request, *args, **kwargs):
        emp = getattr(request.user, "employee_profile", None)

        if emp and emp.role == "HR":
            return view_func(request, *args, **kwargs)

        return HttpResponseForbidden("HR access only")
    return wrapper
