from django.shortcuts import render
from base.models import Product
from django.core.paginator import Paginator

def inventory_view(request):
    products = Product.objects.all()
    
    # Handle search
    q = request.GET.get('q')
    if q:
        products = products.filter(name__icontains=q)
    # Handle sorting
    sort_by = request.GET.get('sort_by')
    if sort_by:
        products = products.order_by(sort_by)
    
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'products': products,
        'page_obj': page_obj
    }
    return render(request, 'inventory.html', context)
