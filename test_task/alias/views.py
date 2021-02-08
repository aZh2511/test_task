from django.shortcuts import render
from django.http import HttpResponse
from .models import Alias


def index(request):
    smth = Alias.objects.all()
    data =[]
    for item in smth:
        data.append((item.alias, item.target, item.start, item.end))
    return HttpResponse(f'{data}')

