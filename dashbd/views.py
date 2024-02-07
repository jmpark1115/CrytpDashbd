from django.shortcuts import render

# Create your views here.

def index(request):
    print('index.html called')
    return render(request, 'dashbd/index.html')

def info(request):
    print('information.html called')
    return render(request, 'dashbd/information2.html')


def info_okx(request):
    print('info okx called')
    return render(request, 'dashbd/info_okx.html')