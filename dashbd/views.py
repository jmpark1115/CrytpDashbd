from django.shortcuts import render

# Create your views here.

def index(request):
    print('index.html called')
    return render(request, 'dashbd/index.html')

def info(request):
    print('information.html called')
    return render(request, 'dashbd/information.html')