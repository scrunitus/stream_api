from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.forms import UserCreationForm
from .models import CreateUserForm
from django.contrib import messages
# Create your views here.

def register(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save() 
            messages.success(request, 'Account created successfully')  
    else:
        form = CreateUserForm()    
    context={"form":form}
    return render(request, "register.html", context)

def login(request):
    return render(request, "login.html")