
import pandas as pd
from django.db import transaction
from .models import Transaction, User, TransactionItem # Import your models

def process_uploaded_transactions(uploaded_file):
    try:
        # Determine file type and read data into a DataFrame
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            return False, "Unsupported file format. Please upload a .csv or .xlsx file."

        # Ensure column names match your expectations

        headers = ['المستخدم', 'نوع المعاملة', 'التاريخ', 'العناصر', 'المجموع']
        required_cols = headers
        if not all(col in df.columns for col in required_cols):
            return False, "File is missing required columns: " + ", ".join(required_cols)

        # Use Django's transaction to ensure all operations succeed or fail together
        with transaction.atomic():
            transactions_created = 0
            for index, row in df.iterrows():
                
                # 1. Look up related objects (User and InventoryItem)
                try:
                    user_obj = User.objects.get(username=row['المستخدم'])
                    item_obj = TransactionItem.objects.get(product=row['العناصر'])
                except (User.DoesNotExist, TransactionItem.DoesNotExist) as e:
                    # Log the error and skip the row or fail the whole transaction
                    raise Exception(f"Related object not found for row {index + 2}: {e}")

                # 2. Create the main Transaction object
                new_transaction = Transaction.objects.create(
                    user=user_obj,
                    type=row['نوع المعاملة'],
                    date=row['التاريخ'], # Pandas can usually handle date parsing
                    amount=row['المجموع']
                )
                
                # 3. Handle Many-to-Many relationships if necessary (e.g., if 'items' is M2M)
                # If Transaction and InventoryItem have a ManyToMany relationship called 'items':
                # new_transaction.items.add(item_obj) 
                
                new_transaction.items.add(item_obj)
                transactions_created += 1

        return True, f"Successfully imported {transactions_created} transactions."

    except Exception as e:
        return False, f"Import failed on row {index + 2}: {e}"