from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, DeleteView
from django.template import loader
from .models import Transaction
from .forms import EditTransactionForm

@login_required
def index(request):
    template = loader.get_template('transactions/transactions_list.html')
    transactions = Transaction.objects.filter(owner=request.user).order_by('-created_date')
    context = {'transactions': transactions}
    return HttpResponse(template.render(context, request))

@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        form = EditTransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = EditTransactionForm(instance=transaction)
    context = {
        'form': form,
        'transaction': transaction,
    }

    return render(request, 'transactions/edit_transaction.html', context)

class TransactionDelete(DeleteView):
    model = Transaction
    success_url = reverse_lazy('index')

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = EditTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.owner = request.user
            transaction.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = EditTransactionForm()
    return render(request, 'transactions/edit_transaction.html', {'form': form})



# Create your views here.
