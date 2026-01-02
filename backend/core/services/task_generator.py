"""
Task Generator Service - Automatic task creation for pharmacy CRM.

Handles:
- Replenishment reminders (product about to run out)
- VIP customer follow-ups
- Churn prevention tasks
- Seasonal dermo recommendations
"""
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

from ..models import Customer, Product, SalesTransaction, Task


class TaskGeneratorService:
    """Otomatik görev oluşturma servisi."""

    def generate_replenishment_tasks(self) -> dict:
        """Ürün bitiş hatırlatma görevleri oluştur.

        Mantık:
        - Son satış tarihi + ürün kullanım süresi - 5 gün = hatırlatma tarihi
        - Bugün veya geçmiş tarihli hatırlatmalar için görev oluştur
        """
        today = timezone.now().date()
        created = 0

        # Son 60 günde satış yapılmış tüm işlemleri al
        recent_sales = SalesTransaction.objects.filter(
            sale_date__gte=today - timedelta(days=60)
        ).select_related('customer', 'product')

        for sale in recent_sales:
            if not sale.product.usage_duration:
                continue

            # Hatırlatma tarihi hesapla
            reminder_date = sale.sale_date + timedelta(
                days=sale.product.usage_duration - 5
            )

            # Geçmiş veya bugün ise görev oluştur
            if reminder_date <= today:
                # Aynı müşteri-ürün için bekleyen görev var mı kontrol et
                existing = Task.objects.filter(
                    customer=sale.customer,
                    product=sale.product,
                    task_type='REPLENISHMENT',
                    status__in=['PENDING', 'IN_PROGRESS']
                ).exists()

                if not existing:
                    Task.objects.create(
                        task_type='REPLENISHMENT',
                        customer=sale.customer,
                        product=sale.product,
                        title=f"Ürün Hatırlatma: {sale.product.name}",
                        description=f"{sale.customer.full_name} müşterisinin {sale.product.name} ürünü bitmek üzere. "
                                    f"Son alım: {sale.sale_date.strftime('%d/%m/%Y')}",
                        priority='MEDIUM',
                        points_value=10,
                        due_date=today,
                    )
                    created += 1

        return {'created': created}

    def generate_churn_prevention_tasks(self) -> dict:
        """Kayıp önleme görevleri oluştur.

        Mantık:
        - Churn risk >= 50 olan müşteriler için görev oluştur
        - Zaten bekleyen görev varsa atla
        """
        today = timezone.now().date()
        created = 0

        at_risk_customers = Customer.objects.filter(
            churn_risk__gte=50
        ).exclude(segment='LOST')

        for customer in at_risk_customers:
            existing = Task.objects.filter(
                customer=customer,
                task_type='CHURN_PREVENTION',
                status__in=['PENDING', 'IN_PROGRESS']
            ).exists()

            if not existing:
                if customer.churn_risk >= 75:
                    priority = 'HIGH'
                    points = 20
                else:
                    priority = 'MEDIUM'
                    points = 15

                Task.objects.create(
                    task_type='CHURN_PREVENTION',
                    customer=customer,
                    title=f"Kayıp Önleme: {customer.full_name}",
                    description=f"Müşteri {customer.churn_risk}% kayıp riski taşıyor. "
                                f"Son ziyaret: {customer.last_visit_date.strftime('%d/%m/%Y') if customer.last_visit_date else 'Bilinmiyor'}",
                    priority=priority,
                    points_value=points,
                    due_date=today,
                )
                created += 1

        return {'created': created}

    def generate_vip_followup_tasks(self) -> dict:
        """VIP müşteri takip görevleri.

        Mantık:
        - VIP/Dermo VIP müşteriler için periyodik takip
        - Son 30 gün içinde görev yoksa yeni görev oluştur
        """
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        created = 0

        vip_customers = Customer.objects.filter(
            segment__in=['VIP', 'DERMO_VIP']
        )

        for customer in vip_customers:
            # Son 30 günde VIP takip görevi var mı?
            recent_task = Task.objects.filter(
                customer=customer,
                task_type='VIP_FOLLOWUP',
                created_at__date__gte=thirty_days_ago
            ).exists()

            if not recent_task:
                is_dermo = customer.segment == 'DERMO_VIP'

                Task.objects.create(
                    task_type='VIP_FOLLOWUP',
                    customer=customer,
                    title=f"VIP Takip: {customer.full_name}",
                    description=f"{'Dermo-Kozmetik ' if is_dermo else ''}VIP müşteri takibi. "
                                f"Toplam puan: {customer.total_points:,.0f}",
                    priority='MEDIUM',
                    points_value=15 if is_dermo else 10,
                    due_date=today + timedelta(days=7),
                )
                created += 1

        return {'created': created}

    def generate_seasonal_dermo_tasks(self) -> dict:
        """Mevsimsel dermo önerileri.

        Mantık:
        - Ekim ve Mayıs aylarında dermo müşterilerine özel öneriler
        """
        today = timezone.now().date()
        month = today.month
        created = 0

        # Sadece Ekim (10) ve Mayıs (5) aylarında çalış
        if month not in [5, 10]:
            return {'created': 0}

        season = 'Yaz' if month == 5 else 'Kış'

        dermo_customers = Customer.objects.filter(
            segment='DERMO_VIP'
        )

        for customer in dermo_customers:
            # Bu ay görev oluşturulmuş mu?
            existing = Task.objects.filter(
                customer=customer,
                task_type='DERMO_CONSULT',
                created_at__month=month,
                created_at__year=today.year
            ).exists()

            if not existing:
                Task.objects.create(
                    task_type='DERMO_CONSULT',
                    customer=customer,
                    title=f"{season} Bakım Önerisi: {customer.full_name}",
                    description=f"Mevsim geçişi için dermo-kozmetik bakım önerisi. "
                                f"{season} için cilt bakım rutini.",
                    priority='MEDIUM',
                    points_value=15,
                    due_date=today + timedelta(days=14),
                )
                created += 1

        return {'created': created}

    def generate_all_tasks(self) -> dict:
        """Tüm otomatik görevleri oluştur."""
        results = {
            'replenishment': self.generate_replenishment_tasks(),
            'churn_prevention': self.generate_churn_prevention_tasks(),
            'vip_followup': self.generate_vip_followup_tasks(),
            'seasonal_dermo': self.generate_seasonal_dermo_tasks(),
        }

        total_created = sum(r.get('created', 0) for r in results.values())
        return {
            'total_created': total_created,
            'details': results
        }
