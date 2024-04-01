from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib import messages


@login_required(login_url='accounts:login')
def home_view(request):
    return render(request, 'home.html')


@login_required(login_url='accounts:login')
def register_view(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save()
            login(request, new_user) 
            return redirect('home')
    else:
        user_form = UserCreationForm()
    return render(request, 'register.html', {'user_form': user_form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts:home')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        login_form = AuthenticationForm()

    return render(request, 'login.html', {'login_form': login_form})



def logout_view(request):
    logout(request)
    return redirect('accounts:login')
