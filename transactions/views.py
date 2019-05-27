from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.template import loader
from .models import Transaction, Account
from .forms import EditTransactionForm, CreateAccountForm

@login_required
def index(request):
    template = loader.get_template('transactions/transactions_list.html')
    transactions = Transaction.objects.filter(owner=request.user, is_initial=False).order_by('-created_date')
    accounts = Account.objects.filter(holder=request.user).order_by('-created_date')
    context = {
        'transactions': transactions,
        'accounts': accounts,
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
    accounts = Account.objects.filter(holder=request.user).order_by('-created_date')
    context = {
        'form': form,
        'transaction': transaction,
        'accounts': accounts,
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
    accounts = Account.objects.filter(holder=request.user).order_by('-created_date')
    return render(request, 'transactions/edit_transaction.html', {'form': form, 'accounts': accounts})

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
def add_account(request):
    account_instance = Account.objects.create();
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            account_instance.holder = request.user
            account_instance.created_date = form.cleaned_data['created_date']
            account_instance.title = form.cleaned_data['title']
            account_instance.save()
            transaction = makeinitialtransaction(account_instance, form.cleaned_data['initial_balance'])
            transaction.owner = request.user
            transaction.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = CreateAccountForm()
    accounts = Account.objects.filter(holder=request.user).order_by('-created_date')
    return render(request, 'transactions/create_account.html', {'form': form, 'accounts': accounts})

class AccountDelete(DeleteView):
    model = Account
    success_url = reverse_lazy('index')

class AccountUpdate(UpdateView):
    model = Account
    fields = ['created_date', 'title', ]
    success_url = reverse_lazy('index')





# Create your views here.
