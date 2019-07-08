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
from .forms import EditTransactionForm, CreateAccountForm, EditSaveUp



def get_current_period(request):
    today = datetime.datetime.now()
    periods = Period.objects.filter(owner=request.user, starts_at__lte=today, ends_at__gte=today)
    if periods.count()>0:
        current_period = periods[0:1].get()
    else:
        current_period = "You still have no plans..."
    return current_period

def get_plans(request):
    period = get_current_period(request)
    if period == "You still have no plans...":
        plans = MandatoryTransaction.objects.none()
    else:
        plans = period.mandatorytransaction_set.all()
    return plans

def do_have_plan(request):
    period = get_current_period(request)
    if period == "You still have no plans...":
        return False
    else:
        return True

def get_not_completed_plans(request):
    plans = get_plans(request)
    completed =[]
    for plan in plans:
        if plan.is_completed():
            completed.append(plan.pk)
    cur_plans = plans.exclude(pk__in=completed) 
    
    return cur_plans

def get_deviations(request):
    plans = get_plans(request)
    completed =[]
    for plan in plans:
        if plan.is_completed():
            completed.append(plan.pk)
    com_plans = plans.filter(pk__in=completed)
    deviations = []
    for com_plan in com_plans:
        last_commit = com_plan.transaction_set.last()
        if com_plan.transaction_type == '+':
            delta = -1 * com_plan.money_left()
        else:
            delta = com_plan.money_left()
        deviation = {'date': last_commit.created_date.date(), 'deviation': delta} 
        deviations.append(deviation)
    return deviations  


def makelistofdays(since, transactions, current_period, request):
    today = datetime.datetime.now().date()
    if current_period != "You still have no plans...":
        since = current_period.starts_at
        per_day = current_period.daylimit()
    else:
        since = since.date()
        per_day = 0
    delta = (today-since).days+1
    listofdays = []
    prev_result = 0
    
    for i in range(delta):
        date = since+ datetime.timedelta(days=i)
        sum=0
        transactionsofday = transactions.filter(created_date__day=date.day, created_date__month=date.month, created_date__year=date.year)
        for transaction in transactionsofday:
            if not transaction.is_planned():
                if transaction.account.account_type == 'active':
                    sum += float(transaction.transaction_type+str(transaction.amount))
                else:
                    sum -= float(transaction.transaction_type+str(transaction.amount))
        deviations = get_deviations(request)
        for deviation in deviations:
            if deviation["date"] == date:
                sum += float(deviation["deviation"])
        available_sum = per_day+prev_result
        day_result = available_sum+sum
        prev_result = day_result
        thisday = {"date": date, "available": available_sum, "sum": sum, 'result': day_result, 'transactionsofday': transactionsofday}
        listofdays.insert(0,thisday)
    return listofdays
    


@login_required
def index(request):
    template = loader.get_template('transactions/transactions_list.html')
    transactions = Transaction.objects.filter(owner=request.user, is_initial=False).order_by('-created_date')
    accounts = Account.objects.filter(holder=request.user).exclude(account_type='passive').order_by('-created_date')
    savings = Account.objects.filter(holder=request.user, account_type='passive').order_by('-created_date')
    since = datetime.datetime(2019,5,1,0,0,0)
    current_period = get_current_period(request)
    plans = get_plans(request)
    have_plan = do_have_plan(request)
    days = makelistofdays(since, transactions, current_period, request)
    context = {
        'transactions': transactions,
        'accounts': accounts,
        'savings': savings,
        'days': days,
        'have_plan': have_plan,
        'current_period': current_period,
        'plans': plans
    }
    return HttpResponse(template.render(context, request))

@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    plans = get_not_completed_plans(request) 
    if transaction.is_planned():
        plans = plans| MandatoryTransaction.objects.filter(pk = transaction.planned_transaction.pk)
    if request.method == 'POST':
        if transaction.account.account_type == 'active':
            form = EditTransactionForm(request.POST, instance=transaction, request=request, plans = plans)
        else:
            form = EditSaveUp(request.POST, instance=transaction, request=request)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        if transaction.account.account_type == 'active':
            form = EditTransactionForm(instance=transaction, request=request, plans = plans)
        else:
            form = EditSaveUp(instance=transaction, request=request)
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
def add_transaction(request, tr_type):
    plans = get_not_completed_plans(request)
    if request.method == 'POST':
        if tr_type == 'save_up':
            form = EditSaveUp(request.POST, request=request)    
        else:
            form = EditTransactionForm(request.POST, request=request, plans = plans)
        
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.owner = request.user
            transaction.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        if tr_type == 'save_up':
            form = EditSaveUp(request=request)
        else:
            form = EditTransactionForm(request=request, plans = plans)
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
