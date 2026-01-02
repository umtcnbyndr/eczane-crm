# Generated manually for Brand model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Marka Adı')),
                ('category', models.CharField(choices=[('DERMO', 'Dermo-Kozmetik'), ('ILAC', 'İlaç'), ('VITAMIN', 'Vitamin/Takviye'), ('MAMA', 'Mama'), ('OTHER', 'Diğer')], default='OTHER', max_length=20, verbose_name='Kategori')),
                ('is_premium', models.BooleanField(default=False, verbose_name='Premium Marka')),
                ('product_count', models.IntegerField(default=0, verbose_name='Ürün Sayısı')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma')),
            ],
            options={
                'verbose_name': 'Marka',
                'verbose_name_plural': 'Markalar',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_code', models.CharField(max_length=50, unique=True, verbose_name='Müşteri Kodu')),
                ('first_name', models.CharField(max_length=100, verbose_name='Ad')),
                ('last_name', models.CharField(max_length=100, verbose_name='Soyad')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Telefon')),
                ('phone_secondary', models.CharField(blank=True, max_length=20, null=True, verbose_name='İkinci Telefon')),
                ('total_points', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Toplam Puan')),
                ('points_tl_value', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Puan TL Karşılığı')),
                ('segment', models.CharField(choices=[('VIP', 'VIP Müşteri'), ('DERMO_VIP', 'Dermo-Kozmetik VIP'), ('STANDARD', 'Standart'), ('NEW', 'Yeni Müşteri'), ('LOST', 'Kayıp Müşteri')], default='STANDARD', max_length=20, verbose_name='Segment')),
                ('churn_risk', models.IntegerField(default=0, verbose_name='Kayıp Riski (%)')),
                ('last_visit_date', models.DateField(blank=True, null=True, verbose_name='Son Ziyaret Tarihi')),
                ('total_spending', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Toplam Harcama')),
                ('dermo_spending', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Dermo Harcama')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncellenme')),
            ],
            options={
                'verbose_name': 'Müşteri',
                'verbose_name_plural': 'Müşteriler',
                'ordering': ['-total_points'],
            },
        ),
        migrations.CreateModel(
            name='ExcelUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='excel_uploads/', verbose_name='Dosya')),
                ('file_name', models.CharField(max_length=255, verbose_name='Dosya Adı')),
                ('file_type', models.CharField(choices=[('CUSTOMER_POINTS', 'Müşteri Puan Raporu'), ('PRODUCT_SALES', 'Ürün Satış Raporu'), ('CUSTOMER_SALES', 'Müşteri Satış Raporu')], max_length=20, verbose_name='Dosya Tipi')),
                ('status', models.CharField(choices=[('PENDING', 'Bekliyor'), ('PROCESSING', 'İşleniyor'), ('COMPLETED', 'Tamamlandı'), ('FAILED', 'Başarısız')], default='PENDING', max_length=20, verbose_name='Durum')),
                ('rows_processed', models.IntegerField(default=0, verbose_name='İşlenen Satır')),
                ('rows_failed', models.IntegerField(default=0, verbose_name='Başarısız Satır')),
                ('error_message', models.TextField(blank=True, verbose_name='Hata Mesajı')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Yüklenme')),
                ('processed_at', models.DateTimeField(blank=True, null=True, verbose_name='İşlenme')),
            ],
            options={
                'verbose_name': 'Excel Yükleme',
                'verbose_name_plural': 'Excel Yüklemeleri',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Ad Soyad')),
                ('role', models.CharField(choices=[('ECZACI', 'Eczacı'), ('TEKNISYEN', 'Teknisyen'), ('KASIYER', 'Kasiyer')], max_length=20, verbose_name='Rol')),
                ('xp_points', models.IntegerField(default=0, verbose_name='XP Puanı')),
                ('tasks_completed', models.IntegerField(default=0, verbose_name='Tamamlanan Görev')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma')),
            ],
            options={
                'verbose_name': 'Personel',
                'verbose_name_plural': 'Personeller',
                'ordering': ['-xp_points'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('barcode', models.CharField(max_length=50, unique=True, verbose_name='Barkod')),
                ('product_code', models.CharField(blank=True, max_length=50, verbose_name='Ürün Kodu')),
                ('name', models.CharField(max_length=255, verbose_name='Ürün Adı')),
                ('category', models.CharField(choices=[('ILAC', 'İlaç'), ('DERMO', 'Dermo-Kozmetik'), ('OTC', 'OTC'), ('MAMA', 'Mama'), ('VITAMIN', 'Vitamin/Takviye'), ('OTHER', 'Diğer')], default='OTHER', max_length=20, verbose_name='Kategori')),
                ('kdv_rate', models.IntegerField(default=10, verbose_name='KDV Oranı')),
                ('stock_quantity', models.IntegerField(default=0, verbose_name='Stok Adedi')),
                ('unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Birim Fiyat')),
                ('usage_duration', models.IntegerField(default=30, help_text='Bir kutu/paket kaç günde biter?', verbose_name='Kullanım Süresi (gün)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncellenme')),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='core.brand', verbose_name='Marka')),
            ],
            options={
                'verbose_name': 'Ürün',
                'verbose_name_plural': 'Ürünler',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Başlık')),
                ('description', models.TextField(blank=True, verbose_name='Açıklama')),
                ('task_type', models.CharField(choices=[('REPLENISHMENT', 'Ürün Hatırlatma'), ('CAMPAIGN', 'Kampanya'), ('FOLLOWUP', 'Takip'), ('CHURN_PREVENTION', 'Kayıp Önleme')], max_length=20, verbose_name='Görev Tipi')),
                ('priority', models.CharField(choices=[('HIGH', 'Yüksek'), ('MEDIUM', 'Orta'), ('LOW', 'Düşük')], default='MEDIUM', max_length=10, verbose_name='Öncelik')),
                ('status', models.CharField(choices=[('PENDING', 'Bekliyor'), ('IN_PROGRESS', 'Devam Ediyor'), ('COMPLETED', 'Tamamlandı'), ('CANCELLED', 'İptal')], default='PENDING', max_length=20, verbose_name='Durum')),
                ('due_date', models.DateField(verbose_name='Son Tarih')),
                ('xp_reward', models.IntegerField(default=10, verbose_name='XP Ödülü')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Tamamlanma')),
                ('notes', models.TextField(blank=True, verbose_name='Notlar')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to='core.staff', verbose_name='Atanan')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='core.customer', verbose_name='Müşteri')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='core.product', verbose_name='Ürün')),
            ],
            options={
                'verbose_name': 'Görev',
                'verbose_name_plural': 'Görevler',
                'ordering': ['due_date', '-priority'],
            },
        ),
        migrations.CreateModel(
            name='SalesTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sale_date', models.DateField(verbose_name='Satış Tarihi')),
                ('quantity', models.IntegerField(default=1, verbose_name='Adet')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Birim Fiyat')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Toplam Tutar')),
                ('kdv_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='KDV Tutarı')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='core.customer', verbose_name='Müşteri')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='core.product', verbose_name='Ürün')),
            ],
            options={
                'verbose_name': 'Satış İşlemi',
                'verbose_name_plural': 'Satış İşlemleri',
                'ordering': ['-sale_date'],
            },
        ),
    ]
