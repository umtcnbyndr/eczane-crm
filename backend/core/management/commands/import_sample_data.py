"""
Management command to import sample data for testing.
"""
import random
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Customer, Product, SalesTransaction, Staff, Task


class Command(BaseCommand):
    help = 'Test için örnek veri oluştur'

    def add_arguments(self, parser):
        parser.add_argument(
            '--customers',
            type=int,
            default=50,
            help='Oluşturulacak müşteri sayısı'
        )
        parser.add_argument(
            '--products',
            type=int,
            default=30,
            help='Oluşturulacak ürün sayısı'
        )

    def handle(self, *args, **options):
        self.stdout.write('Örnek veriler oluşturuluyor...')

        # Personel oluştur
        staff_names = ['Ayşe Yılmaz', 'Mehmet Demir', 'Fatma Kaya', 'Ali Çelik']
        staff_list = []
        for name in staff_names:
            staff, _ = Staff.objects.get_or_create(
                name=name,
                defaults={'total_points': random.randint(100, 1000)}
            )
            staff_list.append(staff)
        self.stdout.write(f'  {len(staff_list)} personel oluşturuldu')

        # Ürünler oluştur
        product_templates = [
            ('ILAC', ['Parol 500mg', 'Aspirin 100mg', 'Majezik 100mg', 'Nurofen 400mg', 'Aferin Forte']),
            ('DERMO', ['La Roche Posay Effaclar', 'Avene Cicalfate', 'Bioderma Sensibio', 'Vichy Mineral 89', 'CeraVe Nemlendirici']),
            ('VITAMIN', ['Supradyn', 'Centrum', 'One A Day', 'Solgar Omega-3', 'Orzax Ocean D3']),
            ('OTC', ['Strepsils', 'Tantum Verde', 'Sudafed', 'Voltaren Emulgel', 'Bepanthen']),
        ]

        products = []
        for category, names in product_templates:
            for name in names:
                barcode = f"869{random.randint(1000000000, 9999999999)}"
                product, _ = Product.objects.get_or_create(
                    barcode=barcode,
                    defaults={
                        'name': name,
                        'category': category,
                        'unit_price': Decimal(random.randint(50, 500)),
                        'stock_quantity': random.randint(5, 100),
                        'usage_duration': 30 if category == 'ILAC' else 60,
                    }
                )
                products.append(product)
        self.stdout.write(f'  {len(products)} ürün oluşturuldu')

        # Müşteriler oluştur
        first_names = ['Ahmet', 'Mehmet', 'Mustafa', 'Ali', 'Hüseyin', 'Ayşe', 'Fatma', 'Zeynep', 'Elif', 'Merve']
        last_names = ['Yılmaz', 'Kaya', 'Demir', 'Çelik', 'Şahin', 'Yıldız', 'Öztürk', 'Aydın', 'Özdemir', 'Arslan']

        customers = []
        for i in range(options['customers']):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            phone = f"053{random.randint(10000000, 99999999)}"

            customer, created = Customer.objects.get_or_create(
                customer_code=f"CUST{i+1:05d}",
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                    'total_points': Decimal(random.randint(0, 50000)),
                    'segment': random.choice(['STANDARD', 'STANDARD', 'VIP', 'DERMO_VIP', 'NEW']),
                }
            )
            customers.append(customer)
        self.stdout.write(f'  {len(customers)} müşteri oluşturuldu')

        # Satışlar oluştur
        today = timezone.now().date()
        transaction_count = 0
        for customer in customers:
            # Her müşteri için rastgele satışlar
            num_transactions = random.randint(0, 10)
            for _ in range(num_transactions):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                sale_date = today - timedelta(days=random.randint(0, 90))

                SalesTransaction.objects.create(
                    customer=customer,
                    product=product,
                    sale_date=sale_date,
                    quantity=quantity,
                    unit_price=product.unit_price,
                    total_amount=product.unit_price * quantity,
                )
                transaction_count += 1

                # Son ziyaret tarihini güncelle
                if not customer.last_visit_date or sale_date > customer.last_visit_date:
                    customer.last_visit_date = sale_date
                    customer.save()

        self.stdout.write(f'  {transaction_count} satış işlemi oluşturuldu')

        # Görevler oluştur
        task_types = ['REMINDER_CALL', 'REPLENISHMENT', 'VIP_FOLLOWUP', 'CHURN_PREVENTION']
        task_count = 0
        for _ in range(20):
            customer = random.choice(customers)
            task_type = random.choice(task_types)

            Task.objects.create(
                task_type=task_type,
                customer=customer,
                title=f"{customer.full_name} - {dict(Task.TYPE_CHOICES).get(task_type)}",
                description=f"Otomatik oluşturulmuş görev",
                status='PENDING',
                priority=random.choice(['LOW', 'MEDIUM', 'HIGH']),
                points_value=random.choice([10, 15, 20]),
                assigned_to=random.choice(staff_list),
                due_date=today + timedelta(days=random.randint(0, 7)),
            )
            task_count += 1

        self.stdout.write(f'  {task_count} görev oluşturuldu')

        self.stdout.write(self.style.SUCCESS('Örnek veriler başarıyla oluşturuldu!'))
