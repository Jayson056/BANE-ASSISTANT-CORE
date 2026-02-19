from django.shortcuts import render

def index(request):
    return render(request, 'bane_landing/index.html')
