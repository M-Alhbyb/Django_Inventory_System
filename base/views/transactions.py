from django.shortcuts import render
from django.db.models import Q
from base.models import Transaction, User
from django.core.paginator import Paginator

def transactions_view(request):
    # Get all transactions
    transactions = Transaction.objects.select_related('user').prefetch_related('items__product').order_by('-date')
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Handle search
    q = request.GET.get('q')
    if q:
        transactions = transactions.filter(
            Q(id__icontains=q) |
            Q(user__username__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q)
        )
    
    # Handle transaction type filter
    transaction_type = request.GET.get('type')
    if transaction_type and transaction_type != 'all':
        transactions = transactions.filter(type=transaction_type)
    
    # Handle user type filter
    user_type = request.GET.get('user_type')
    if user_type and user_type != 'all':
        transactions = transactions.filter(user__user_type=user_type)
    
    # Get statistics
    total_transactions = transactions.count()
    total_take = transactions.filter(type='take').count()
    total_payment = transactions.filter(type='payment').count()
    total_restore = transactions.filter(type='restore').count()
    total_fees = transactions.filter(type='fees').count()
    
    context = {
        'page_obj': page_obj,
        'total_transactions': total_transactions,
        'total_take': total_take,
        'total_payment': total_payment,
        'total_restore': total_restore,
        'total_fees': total_fees,
        'current_type': transaction_type if transaction_type else 'all',
        'current_user_type': user_type if user_type else 'all',
        'search_query': q if q else '',
    }
    
    return render(request, 'transactions.html', context)
