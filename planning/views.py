import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.utils import timezone
from django.template import loader
from django.db import transaction
from django.forms import inlineformset_factory, formset_factory, modelformset_factory
from .models import Period
from transactions.models import Account, Transaction
from .forms import MandatoryTransactionFormSet, MandatoryTransactionFormSetEdit, PeriodGoalForm, SavingsDistributionForm

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
            return HttpResponseRedirect(reverse('check_balances', kwargs={'pk': self.object.pk}))
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
            return HttpResponseRedirect(reverse('check_balances', kwargs={'pk': self.object.pk}))
        return super(PeriodMandatoryTransactionUpdate, self).form_valid(form)

def get_date_balances(request, day):
    accounts = Account.objects.filter(holder=request.user)
    balances =[]
    for account in accounts:
        balance = {'title': account.title, 'date_balance': account.date_balance(day)}
        balances.append(balance)
    return balances



def check_balances(request, pk):
    period = get_object_or_404(Period, pk=pk)

    accounts = Account.objects.filter(holder=request.user).exclude(account_type='passive').order_by('-created_date')
    savings = Account.objects.filter(holder=request.user, account_type='passive').order_by('-created_date')
    balances = get_date_balances(request, period.starts_at)
    context = {
        'accounts': accounts,
        'savings': savings,
        'period': period,
        'balances': balances
    }

    return render(request, 'planning/check_balance.html', context)

def prepare_initial_distribution(savings):
    initial = []
    for saving in savings:
        initial.append({'account': Account.objects.get(pk=saving.pk), 'amount': 0})
    return initial


def finish_the_period(request, pk):
    period = get_object_or_404(Period, pk=pk)
    period.ends_at = datetime.date.today()
    savings = Account.objects.filter(holder=request.user, account_type='passive').order_by('-created_date')
    initial_data = prepare_initial_distribution(savings)
    SavingsDistributionFormset = modelformset_factory(Transaction, fields=('account', 'amount'), extra=len(initial_data))
    if request.method == 'POST':
        formset = SavingsDistributionFormset(request.POST, queryset = Transaction.objects.none(), initial = initial_data)
        if formset.is_valid():
            period.save()
            for form in formset:
                if form.is_valid():
                    new_transaction = form.save()
                    new_transaction.created_date = datetime.datetime.combine(datetime.date.today(), datetime.datetime.max.time())
                    new_transaction.owner = request.user
                    new_transaction.transaction_type = '+'
                    new_transaction.comment = 'Finish the period'
                    new_transaction.save()
            # do something with the formset.cleaned_data
            return HttpResponseRedirect(reverse('index'))
    else:
        formset = SavingsDistributionFormset(queryset = Transaction.objects.none(), initial = initial_data)
    

    accounts = Account.objects.filter(holder=request.user).exclude(account_type='passive').order_by('-created_date')
    balances = get_date_balances(request, period.starts_at)
    context = {
        'accounts': accounts,
        'savings': savings,
        'period': period,
        'formset': formset,
    }

    return render(request, 'planning/finish_period.html', context)

    

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

