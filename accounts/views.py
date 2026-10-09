from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name="Admin").exists():
            return redirect("admin_dashboard")

        if request.user.groups.filter(name="Customer").exists():
            return redirect("customer_dashboard")

        logout(request)
        messages.error(
            request,
            "Your account does not have an assigned application role.",
        )
        return redirect("accounts:login")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            messages.error(
                request,
                "Invalid username or password.",
            )
            return render(request, "accounts/login.html")

        if user.groups.filter(name="Admin").exists():
            login(request, user)
            return redirect("admin_dashboard")

        if user.groups.filter(name="Customer").exists():
            login(request, user)
            return redirect("customer_dashboard")

        messages.error(
            request,
            "Your account does not have an assigned application role.",
        )

    return render(request, "accounts/login.html")


@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("accounts:login")