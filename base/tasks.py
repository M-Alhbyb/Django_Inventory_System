from celery import shared_task
from base.models import TransactionItem, Product
from prophet import Prophet
import pandas as pd


def forecast_stock(product_id, days=30):
    if TransactionItem.objects.filter(product_id=product_id).count() < 2:
        return None
    # تحميل البيانات من Django
    qs = TransactionItem.objects.filter(product_id=product_id).order_by("transaction__date")

    df = pd.DataFrame(list(qs.values("transaction__date", "quantity")))
    df.rename(columns={"transaction__date": "ds", "quantity": "y"}, inplace=True)

    # Remove timezone information as Prophet requires timezone-naive datetimes
    if not df.empty:
        df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)

    # إنشاء النموذج
    model = Prophet()
    model.fit(df)

    # تحديد مدة التنبؤ
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)

    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]


def estimate_stock_out(product_id=-1, forecast_df=None):
    if product_id == -1 or forecast_df is None:
        products = Product.objects.all()
        for product in products:
            if TransactionItem.objects.filter(product_id=product.id).count() < 2:
                continue
            forecast_df = forecast_stock(product.id)
            if forecast_df is not None:
                total = 0
                for _, row in forecast_df.iterrows():
                    total += max(row['yhat'], 0)

                    if total >= product.stock:
                        product.estimated_stock_out = row['ds']
                        product.save()
                        break
    return None

@shared_task
def estimate_stock_out_task():
    estimate_stock_out()
    return {'status': 'done', 'result': 'Process completed successfully!'} 