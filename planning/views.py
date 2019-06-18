import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.utils import timezone
from django.template import loader
from django.db import transaction
from .models import Period
from transactions.models import Account
from .forms import MandatoryTransactionFormSet, MandatoryTransactionFormSetEdit, PeriodGoalForm

# Create your views here.
class PeriodCreate(CreateView):
    model = Period
    fields = ['starts_at', 'ends_at']

class PeriodMandatoryTransactionCreate(CreateView):
    model = Period
    fields = ['starts_at', 'ends_at']
    

    def get_context_data(self, **kwargs):
        data = super(PeriodMandatoryTransactionCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['mandatorytransactions'] = MandatoryTransactionFormSet(self.request.POST)
        else:
            data['mandatorytransactions'] = MandatoryTransactionFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        mandatorytransactions = context['mandatorytransactions']
        with transaction.atomic():
            form.instance.owner = self.request.user
            self.object = form.save()
            if mandatorytransactions.is_valid():
                mandatorytransactions.instance = self.object
                mandatorytransactions.save()
            return HttpResponseRedirect(reverse('set_goal', kwargs={'pk': self.object.pk}))
        return super(PeriodMandatoryTransactionCreate, self).form_valid(form)

class PeriodUpdate(UpdateView):
    model = Period
    fields = ['starts_at', 'ends_at']


class PeriodMandatoryTransactionUpdate(UpdateView):
    model = Period
    fields = ['starts_at', 'ends_at']

    def get_context_data(self, **kwargs):
        data = super(PeriodMandatoryTransactionUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['mandatorytransactions'] = MandatoryTransactionFormSetEdit(self.request.POST, instance=self.object)
        else:
            data['mandatorytransactions'] = MandatoryTransactionFormSetEdit(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        mandatorytransactions = context['mandatorytransactions']
        with transaction.atomic():
            self.object = form.save()
            if mandatorytransactions.is_valid():
                mandatorytransactions.instance = self.object
                mandatorytransactions.save()
            return HttpResponseRedirect(reverse('set_goal', kwargs={'pk': self.object.pk}))
        return super(PeriodMandatoryTransactionUpdate, self).form_valid(form)
    

def set_the_goal(request, pk):
    period = get_object_or_404(Period, pk=pk)
    
    if request.method == 'POST':
        form = PeriodGoalForm(request.POST)
        if form.is_valid():
            period.goal = form.cleaned_data['goal']
            period.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = PeriodGoalForm()
    accounts = Account.objects.filter(holder=request.user).exclude(account_type='passive').order_by('-created_date')
    savings = Account.objects.filter(holder=request.user, account_type='passive').order_by('-created_date')
    context = {
        'form': form,
        'accounts': accounts,
        'savings': savings,
        'period': period,
    }

    return render(request, 'planning/setting_goal.html', context)

