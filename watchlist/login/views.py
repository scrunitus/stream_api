from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .models import CreateUserForm
from django.contrib import messages

# Create your views here.

def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get("username")
            messages.success(request, f'Account created successfully for {user}')
            return redirect("login")
    else:
        form = CreateUserForm()    
    context={"form":form}
    return render(request, "register.html", context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.info(request, "Username OR password is incorrect")
    return render(request, "login.html")

def logout_user(request):
    logout(request)
    return redirect("login")