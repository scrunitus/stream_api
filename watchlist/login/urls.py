from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path("register/", views.register, name="register"),
    path("login/", views.loginPage, name="login"),
    path("logout", views.logout_user, name="logout"),
]