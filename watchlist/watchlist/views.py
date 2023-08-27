from django.shortcuts import redirect


def index(requests):
    return redirect("login")