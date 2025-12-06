from django.shortcuts import render
from prophet import Prophet
import pandas as pd
from base.models import TransactionItem, Product
from datetime import datetime
from django.core.paginator import Paginator
from base.tasks import estimate_stock_out_task
from django.http import JsonResponse

def ai_view(request):
    #estimate_stock_out()
    paginator = Paginator(Product.objects.all().order_by('estimated_stock_out'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    current_date = datetime.now()
    context = {
      'page_obj': page_obj,
      'current_date': current_date
    }
    return render(request, 'ai.html', context)

def get_process_status(request, task_id):
    task = estimate_stock_out_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state, 'progress': 0}
    elif task.state == 'PROGRESS':
        progress = (task.info.get('current', 0) / task.info.get('total', 1)) * 100
        response = {'state': task.state, 'progress': round(progress)}
    elif task.state == 'SUCCESS':
        response = {'state': task.state, 'progress': 100, 'result': task.result}
    else:
        response = {'state': task.state, 'progress': 0, 'error': str(task.info)}
    return JsonResponse(response)

def ai_refresh(request):
    task = estimate_stock_out_task.delay()
    return JsonResponse({'task_id': task.id})