from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date

from .forms import TransactionForm
from .models import Transaction, UserBalance
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect


@login_required
def index(request):
    transactions = Transaction.objects.filter(user=request.user)
    recent_transactions = transactions.order_by('-date')[:3]
    balance = request.user.balance.balance
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()

            if transaction.type == 'income':
                request.user.balance.balance += transaction.amount
            elif transaction.type == 'expense':
                request.user.balance.balance -= transaction.amount
            request.user.balance.save()

            return redirect('index')
    else:
        form = TransactionForm()

    context = {
        'transactions': transactions,
        'form': form,
        'balance': balance,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'index.html', context)

@login_required()
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        transactions = transactions.filter(
            date__range=[parse_date(start_date), parse_date(end_date)]
        )

    return render(request, 'transaction_list.html', {'transactions': transactions})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            UserBalance.objects.create(user=user)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

