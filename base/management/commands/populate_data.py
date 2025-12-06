import random
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from base.models import Category, Product, User, Transaction, TransactionItem

# Initialize Faker with Arabic locale
fake = Faker(['ar_AA', 'ar_EG', 'ar_SA'])

# Predefined realistic data for better logic
CATEGORIES_DATA = {
    "هواتف ذكية": [
        "آيفون 14 برو", "آيفون 13", "سامسونج جالاكسي S23", "سامسونج جالاكسي A54", 
        "شاومي ريدمي نوت 12", "أوبو رينو 8", "جوجل بيكسل 7", "هواوي P60 برو"
    ],
    "أجهزة لابتوب": [
        "ماك بوك آير M2", "ماك بوك برو 14", "ديل XPS 13", "اتش بي سبيكتر", 
        "لينوفو ثينك باد", "أسوس زين بوك", "إيسر سويفت"
    ],
    "أجهزة منزلية": [
        "غسالة إل جي 7 كيلو", "ثلاجة سامسونج 18 قدم", "ميكروويف باناسونيك", 
        "خلاط مولينكس", "مكنسة كهربائية دايسون", "تكييف شارب 1.5 حصان"
    ],
    "شاشات وتلفزيون": [
        "شاشة سامسونج 55 بوصة 4K", "شاشة إل جي OLED", "شاشة سوني برافيا", 
        "شاشة توشيبا سمارت"
    ],
    "ملابس رجالي": [
        "قميص قطن كلاسيك", "بنطلون جينز أزرق", "تيشيرت بولو", "بدلة رسمية سوداء", 
        "جاكيت جلد طبيعي"
    ],
    "ملابس حريمي": [
        "فستان سهرة", "بلوزة حرير", "تنورة طويلة", "عباية سوداء مطرزة", 
        "حذاء كعب عالي"
    ],
    "عطور ومستحضرات": [
        "عطر ديور سوفاج", "عطر شانيل رقم 5", "عطر بلو دي شانيل", "مجموعة مكياج كاملة", 
        "كريم ترطيب بشرة"
    ],
    "ألعاب فيديو": [
        "بلايستيشن 5", "اكس بوكس سيريس اكس", "نينتندو سويتش", "ذراع تحكم بلايستيشن", 
        "سماعة جيمنج لوجيتك"
    ],
    "اكسسوارات": [
        "ساعة آبل الجيل الثامن", "سماعة ايربودز برو", "شاحن انكر سريع", 
        "جراب موبايل سيليكون", "باور بانك 10000 ملي أمبير"
    ],
    "أثاث منزلي": [
        "كنبة ركنة مودرن", "طاولة طعام 6 كراسي", "دولاب ملابس كبير", 
        "سرير مزدوج مريح", "مكتب عمل خشبي"
    ]
}

class Command(BaseCommand):
    help = 'Populate database with realistic Arabic data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old data...')
        TransactionItem.objects.all().delete()
        Transaction.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write('Creating realistic data...')
        
        # 1. Create Categories and Products
        all_products = []
        
        for cat_name, products_list in CATEGORIES_DATA.items():
            category = Category.objects.create(
                name=cat_name,
                description=fake.sentence()
            )
            self.stdout.write(f'Created Category: {cat_name}')
            
            for prod_name in products_list:
                # Generate realistic price (e.g., 1000, 1050, 1099)
                base_price = random.randint(10, 5000)
                if base_price > 100:
                    base_price = (base_price // 50) * 50  # Round to nearest 50
                
                price = Decimal(base_price) + Decimal(random.choice(['0.00', '0.99', '0.50']))
                
                product = Product.objects.create(
                    name=prod_name,
                    description=fake.text(max_nb_chars=100),
                    price=price,
                    stock=random.randint(200, 2000),
                    category=category
                )
                all_products.append(product)

        self.stdout.write(f'Total Products Created: {len(all_products)}')

        # 2. Create Users (Merchants and Representatives)
        merchants = []
        representatives = []

        # Create 10 Merchants
        for _ in range(10):
            first_name = fake.first_name_male()
            last_name = fake.last_name()
            username = f"merchant_{random.randint(1000, 9999)}"
            
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123',
                first_name=first_name,
                last_name=last_name,
                phone=fake.phone_number(),
                address=fake.address(),
                user_type='merchant'
            )
            merchants.append(user)

        # Create 10 Representatives
        for _ in range(10):
            first_name = fake.first_name_male()
            last_name = fake.last_name()
            username = f"rep_{random.randint(1000, 9999)}"
            
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123',
                first_name=first_name,
                last_name=last_name,
                phone=fake.phone_number(),
                address=fake.address(),
                user_type='representative'
            )
            representatives.append(user)

        self.stdout.write(f'Created {len(merchants)} Merchants and {len(representatives)} Representatives')

        # 3. Create Transactions
        users = merchants + representatives
        
        # Generate dates for the last 60 days
        end_date = timezone.now()
        
        for user in users:
            self.stdout.write(f'Generating transactions for {user.first_name} {user.last_name}...')
            
            for _ in range(50):
                # Random date
                random_days = random.randint(0, 60)
                tx_date = end_date - timedelta(days=random_days)
                
                # Determine transaction type
                if user.user_type == 'merchant':
                    tx_type = random.choices(
                        ['take', 'payment', 'restore', 'fees'], 
                        weights=[60, 25, 10, 5], 
                        k=1
                    )[0]
                else:
                    tx_type = random.choices(
                        ['take', 'restore', 'fees'], 
                        weights=[80, 15, 5], 
                        k=1
                    )[0]
                
                transaction = Transaction.objects.create(
                    user=user,
                    type=tx_type,
                )
                
                if tx_type in ['take', 'restore']:
                    # Add items
                    num_items = random.randint(1, 4)
                    selected_products = random.sample(all_products, num_items)
                    
                    for product in selected_products:
                        qty = random.randint(1, 5)
                        TransactionItem.objects.create(
                            transaction=transaction,
                            product=product,
                            quantity=qty
                        )
                    
                elif tx_type in ['payment', 'fees']:
                    # Set random amount (Round numbers)
                    amount = Decimal(random.choice([500, 1000, 1500, 2000, 2500, 5000, 10000]))
                    # Add some variance sometimes
                    if random.random() > 0.7:
                         amount += Decimal(random.choice([50, 100, 250]))

                    transaction.amount = amount
                    transaction.save()
                
                # Force update the date at the very end to ensure it sticks
                Transaction.objects.filter(pk=transaction.pk).update(date=tx_date)

        self.stdout.write(self.style.SUCCESS('Successfully populated database with realistic Arabic data'))
