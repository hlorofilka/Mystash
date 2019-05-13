from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader

@login_required
def index(request):
    template = loader.get_template('transactions/transactions_list.html')
    context = {}
    return HttpResponse(template.render(context, request))
# Create your views here.
