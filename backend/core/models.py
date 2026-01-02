"""
Core models for SmartPharmacy CRM.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Brand(models.Model):
    """Marka modeli."""

    CATEGORY_CHOICES = [
        ('DERMO', 'Dermo-Kozmetik'),
        ('ILAC', 'İlaç'),
        ('VITAMIN', 'Vitamin/Takviye'),
        ('MAMA', 'Mama'),
        ('OTHER', 'Diğer'),
    ]

    name = models.CharField('Marka Adı', max_length=100, unique=True)
    category = models.CharField('Kategori', max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    is_premium = models.BooleanField('Premium Marka', default=False)
    product_count = models.IntegerField('Ürün Sayısı', default=0)

    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)

    class Meta:
        verbose_name = 'Marka'
        verbose_name_plural = 'Markalar'
        ordering = ['name']

    def __str__(self):
        return self.name


class Customer(models.Model):
    """Müşteri modeli."""

    SEGMENT_CHOICES = [
        ('VIP', 'VIP Müşteri'),
        ('DERMO_VIP', 'Dermo-Kozmetik VIP'),
        ('STANDARD', 'Standart'),
        ('NEW', 'Yeni Müşteri'),
        ('LOST', 'Kayıp Müşteri'),
    ]

    customer_code = models.CharField('Müşteri Kodu', max_length=50, unique=True)
    first_name = models.CharField('Ad', max_length=100)
    last_name = models.CharField('Soyad', max_length=100)
    phone = models.CharField('Telefon', max_length=20, blank=True, null=True)
    phone_secondary = models.CharField('İkinci Telefon', max_length=20, blank=True, null=True)

    total_points = models.DecimalField('Toplam Puan', max_digits=12, decimal_places=2, default=0)
    points_tl_value = models.DecimalField('Puan TL Karşılığı', max_digits=12, decimal_places=2, default=0)

    segment = models.CharField('Segment', max_length=20, choices=SEGMENT_CHOICES, default='STANDARD')
    churn_risk = models.IntegerField('Kayıp Riski (%)', default=0)  # 0-100 arası

    last_visit_date = models.DateField('Son Ziyaret Tarihi', blank=True, null=True)
    total_spending = models.DecimalField('Toplam Harcama', max_digits=12, decimal_places=2, default=0)
    dermo_spending = models.DecimalField('Dermo Harcama', max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme', auto_now=True)

    class Meta:
        verbose_name = 'Müşteri'
        verbose_name_plural = 'Müşteriler'
        ordering = ['-total_points']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def update_churn_risk(self):
        """Kayıp riskini hesapla (son ziyarete göre)."""
        if not self.last_visit_date:
            self.churn_risk = 100
            return

        days_since_visit = (timezone.now().date() - self.last_visit_date).days

        if days_since_visit <= 30:
            self.churn_risk = 0
        elif days_since_visit <= 60:
            self.churn_risk = 25
        elif days_since_visit <= 90:
            self.churn_risk = 50
        elif days_since_visit <= 120:
            self.churn_risk = 75
        else:
            self.churn_risk = 100
            self.segment = 'LOST'


class Product(models.Model):
    """Ürün modeli."""

    CATEGORY_CHOICES = [
        ('ILAC', 'İlaç'),
        ('DERMO', 'Dermo-Kozmetik'),
        ('OTC', 'OTC'),
        ('MAMA', 'Mama'),
        ('VITAMIN', 'Vitamin/Takviye'),
        ('OTHER', 'Diğer'),
    ]

    barcode = models.CharField('Barkod', max_length=50, unique=True)
    product_code = models.CharField('Ürün Kodu', max_length=50, blank=True)
    name = models.CharField('Ürün Adı', max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='products', verbose_name='Marka')

    category = models.CharField('Kategori', max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    kdv_rate = models.IntegerField('KDV Oranı', default=10)

    stock_quantity = models.IntegerField('Stok Adedi', default=0)
    unit_price = models.DecimalField('Birim Fiyat', max_digits=10, decimal_places=2, default=0)

    usage_duration = models.IntegerField('Kullanım Süresi (gün)', default=30,
                                         help_text='Bir kutu/paket kaç günde biter?')

    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme', auto_now=True)

    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'
        ordering = ['name']

    def __str__(self):
        return self.name


class SalesTransaction(models.Model):
    """Satış işlemi modeli."""

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                 related_name='transactions', verbose_name='Müşteri')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='transactions', verbose_name='Ürün')

    sale_date = models.DateField('Satış Tarihi')
    quantity = models.IntegerField('Adet', default=1)
    unit_price = models.DecimalField('Birim Fiyat', max_digits=10, decimal_places=2)
    total_amount = models.DecimalField('Toplam Tutar', max_digits=12, decimal_places=2)
    kdv_amount = models.DecimalField('KDV Tutarı', max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)

    class Meta:
        verbose_name = 'Satış İşlemi'
        verbose_name_plural = 'Satış İşlemleri'
        ordering = ['-sale_date']

    def __str__(self):
        return f"{self.customer} - {self.product} ({self.sale_date})"

    def calculate_replenishment_date(self):
        """Ürün bitiş tahmin tarihini hesapla."""
        if self.product.usage_duration:
            return self.sale_date + timedelta(days=self.product.usage_duration - 5)
        return None


class Staff(models.Model):
    """Personel modeli (Gamification için)."""

    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='staff_profile', null=True, blank=True)
    name = models.CharField('İsim', max_length=100)

    total_points = models.IntegerField('Toplam Puan (XP)', default=0)
    weekly_points = models.IntegerField('Haftalık Puan', default=0)
    monthly_points = models.IntegerField('Aylık Puan', default=0)

    tasks_completed = models.IntegerField('Tamamlanan Görev', default=0)

    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme', auto_now=True)

    class Meta:
        verbose_name = 'Personel'
        verbose_name_plural = 'Personeller'
        ordering = ['-total_points']

    def __str__(self):
        return self.name

    def add_points(self, points):
        """Personele puan ekle."""
        self.total_points += points
        self.weekly_points += points
        self.monthly_points += points
        self.save()


class Task(models.Model):
    """Görev modeli (Gamification)."""

    TYPE_CHOICES = [
        ('REMINDER_CALL', 'Hatırlatma Araması'),
        ('BIRTHDAY', 'Doğum Günü Kutlaması'),
        ('SPECIAL_DAY', 'Özel Gün Kutlaması'),
        ('DERMO_CONSULT', 'Dermo Danışmanlığı'),
        ('REPLENISHMENT', 'Ürün Bitiş Hatırlatması'),
        ('VIP_FOLLOWUP', 'VIP Takip'),
        ('CHURN_PREVENTION', 'Kayıp Önleme'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Bekliyor'),
        ('IN_PROGRESS', 'Devam Ediyor'),
        ('COMPLETED', 'Tamamlandı'),
        ('UNREACHABLE', 'Ulaşılamadı'),
        ('CANCELLED', 'İptal'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Düşük'),
        ('MEDIUM', 'Orta'),
        ('HIGH', 'Yüksek'),
        ('URGENT', 'Acil'),
    ]

    task_type = models.CharField('Görev Tipi', max_length=20, choices=TYPE_CHOICES)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                 related_name='tasks', verbose_name='Müşteri')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='tasks', verbose_name='Ürün')

    title = models.CharField('Başlık', max_length=200)
    description = models.TextField('Açıklama', blank=True)

    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='PENDING')
    priority = models.CharField('Öncelik', max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')

    points_value = models.IntegerField('Puan Değeri (XP)', default=10)

    assigned_to = models.ForeignKey(Staff, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='assigned_tasks',
                                    verbose_name='Atanan Personel')

    due_date = models.DateField('Son Tarih', null=True, blank=True)
    completed_at = models.DateTimeField('Tamamlanma Zamanı', null=True, blank=True)
    notes = models.TextField('Notlar', blank=True)

    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme', auto_now=True)

    class Meta:
        verbose_name = 'Görev'
        verbose_name_plural = 'Görevler'
        ordering = ['-priority', 'due_date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.customer}"

    def complete(self, staff=None):
        """Görevi tamamla ve puan ekle."""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()

        if staff:
            staff.add_points(self.points_value)
            staff.tasks_completed += 1
            staff.save()


class ExcelUpload(models.Model):
    """Excel dosya yükleme kaydı."""

    FILE_TYPE_CHOICES = [
        ('PRODUCT_SALES', 'Ürün Satış Raporu'),
        ('CUSTOMER_SALES', 'Müşteri Satış Raporu'),
        ('CUSTOMER_POINTS', 'Müşteri Puan Raporu'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Bekliyor'),
        ('PROCESSING', 'İşleniyor'),
        ('COMPLETED', 'Tamamlandı'),
        ('FAILED', 'Hata'),
    ]

    file = models.FileField('Dosya', upload_to='excel_uploads/')
    file_type = models.CharField('Dosya Tipi', max_length=20, choices=FILE_TYPE_CHOICES)
    file_name = models.CharField('Dosya Adı', max_length=255)

    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='PENDING')

    rows_processed = models.IntegerField('İşlenen Satır', default=0)
    rows_failed = models.IntegerField('Hatalı Satır', default=0)
    error_message = models.TextField('Hata Mesajı', blank=True)

    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='excel_uploads')

    created_at = models.DateTimeField('Yükleme Zamanı', auto_now_add=True)
    processed_at = models.DateTimeField('İşlenme Zamanı', null=True, blank=True)

    class Meta:
        verbose_name = 'Excel Yükleme'
        verbose_name_plural = 'Excel Yüklemeleri'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.file_name} ({self.get_status_display()})"
