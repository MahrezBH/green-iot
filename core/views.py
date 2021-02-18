from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

def setup(request):
    return render(request, 'setup.html')

def supported(request):
    return render(request, 'supported.html')
