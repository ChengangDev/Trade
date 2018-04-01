from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import logging


def index(request):
    template = loader.get_template('option/index.html')
    context = {
        'hello': 'world',
    }
    return HttpResponse(template.render(context, request))