from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path("home", views.index, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.loginPage, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("topmovies", views.topmovies, name="topmovies"),
    path("search", views.search, name="search"),
]
