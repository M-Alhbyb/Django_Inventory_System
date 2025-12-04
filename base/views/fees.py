from django.shortcuts import render, redirect
from django.contrib import messages
from base.models import Transaction
from base.forms import FeesForm
from decimal import Decimal


def add_fees(request):
    """
    Handle fees transaction creation.
    Fees are expenses that don't involve products or users.
    """
    if request.method == 'POST':
        form = FeesForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description', '')
            
            # Create the fees transaction
            transaction = Transaction.objects.create(
                user=None,  # Fees don't have a user
                amount=amount,
                type='fees'
            )
            
            # You could store the description in a separate field if needed
            # For now, we'll just create the transaction
            
            messages.success(request, f'تم إضافة منصرف بقيمة {amount} ج.س بنجاح')
            return redirect('base:dashboard')
        else:
            messages.error(request, 'حدث خطأ في البيانات المدخلة')
    
    return redirect('base:dashboard')