from django.shortcuts import render
from django.urls import reverse

# Create your views here.

def index(request):
    print('index.html called')
    url = reverse('optionbd:index')
    print(url)
    return render(request, 'optionbd/index.html')
