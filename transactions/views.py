import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.utils import timezone
from django.template import loader
from .models import Transaction, Account
from planning.models import Period, MandatoryTransaction
from .forms import EditTransactionForm, CreateAccountForm

def makelistofdays(since, transactions):
    today = datetime.datetime.now()
    delta = (today-since).days
    listofdays = []
    for i in range(delta+1):
        date = today - datetime.timedelta(days=i)
        sum=0
        transactionsofday = transactions.filter(created_date__day=date.day, created_date__month=date.month, created_date__year=date.year)
        for transaction in transactionsofday:
            sum += float(transaction.transaction_type+str(transaction.amount))
        thisday = {"date": date, "sum": sum, 'transactionsofday': transactionsofday}
        listofdays.append(thisday)
    return listofdays


@login_required
def index(request):
    template = loader.get_template('transactions/transactions_list.html')
    transactions = Transaction.objects.filter(owner=request.user, is_initial=False).order_by('-created_date')
    accounts = Account.objects.filter(holder=request.user).exclude(account_type='passive').order_by('-created_date')
    savings = Account.objects.filter(holder=request.user, account_type='passive').order_by('-created_date')
    since = datetime.datetime(2019,5,1,0,0,0)
    days = makelistofdays(since, transactions)
    today = datetime.datetime.now()
    periods = Period.objects.filter(owner=request.user, starts_at__lte=today, ends_at__gte=today)
    if periods.count()>0:
        have_plan = True
        current_period = periods[0:1].get()
    else:
        have_plan = False
        current_period = "You still have no plans..."
    context = {
        'transactions': transactions,
        'accounts': accounts,
        'savings': savings,
        'days': days,
        'have_plan': have_plan,
        'current_period': current_period,
    }
    return HttpResponse(template.render(context, request))

@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        form = EditTransactionForm(request.POST, instance=transaction, request=request)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = EditTransactionForm(instance=transaction, request=request)
    accounts = Account.objects.filter(holder=request.user).exclude(account_type='passive').order_by('-created_date')
    savings = Account.objects.filter(holder=request.user, account_type='passive').order_by('-created_date')
    context = {
        'form': form,
        'transaction': transaction,
        'accounts': accounts,
        'savings': savings,
    }

    return render(request, 'transactions/edit_transaction.html', context)

class TransactionDelete(DeleteView):
    model = Transaction
    success_url = reverse_lazy('index')

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = EditTransactionForm(request.POST, request=request)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.owner = request.user
            transaction.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = EditTransactionForm(request=request)
    accounts = Account.objects.filter(holder=request.user).exclude(account_type='passive').order_by('-created_date')
    savings = Account.objects.filter(holder=request.user, account_type='passive').order_by('-created_date')
    return render(request, 'transactions/edit_transaction.html', {'form': form, 'accounts': accounts, 'savings': savings})

def makeinitialtransaction(account, sum):
    transaction = Transaction.objects.create()
    transaction.created_date = account.created_date
    if sum<0:
        transaction.transaction_type = '-'
        transaction.amount = -1 * sum
    else:
        transaction.transaction_type = '+'
        transaction.amount = sum
    transaction.account = account
    transaction.comment = 'Initial operation for account'
    transaction.is_initial = True
    return transaction 


@login_required
def add_account(request, acc_type):
    account_instance = Account.objects.create()
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            account_instance.holder = request.user
            account_instance.created_date = form.cleaned_data['created_date']
            account_instance.title = form.cleaned_data['title']
            account_instance.account_type = acc_type
            account_instance.save()
            transaction = makeinitialtransaction(account_instance, form.cleaned_data['initial_balance'])
            transaction.owner = request.user
            transaction.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = CreateAccountForm()
    accounts = Account.objects.filter(holder=request.user).exclude(account_type='passive').order_by('-created_date')
    savings = Account.objects.filter(holder=request.user, account_type='passive').order_by('-created_date')
    return render(request, 'transactions/create_account.html', {'form': form, 'accounts': accounts, 'savings':savings})

class AccountDelete(DeleteView):
    model = Account
    success_url = reverse_lazy('index')

class AccountUpdate(UpdateView):
    model = Account
    fields = ['created_date', 'title', ]
    success_url = reverse_lazy('index')





# Create your views here.
