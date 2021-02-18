from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# @login_required
def home(request):
    return render(request, 'home.html')

# @login_required
def setup(request):
    return render(request, 'setup.html')

# @login_required
def supported(request):
    return render(request, 'supported.html')
