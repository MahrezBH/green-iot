from django.shortcuts import render
from allauth.account.views import SignupView, LoginView, PasswordResetView


class MyLoginView(LoginView):
    template_name = 'login.html'
