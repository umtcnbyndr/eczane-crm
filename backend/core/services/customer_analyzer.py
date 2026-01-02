"""
Customer Analyzer Service - Customer segmentation and analytics.

Handles:
- Segment classification (VIP, Dermo VIP, Standard, Lost)
- Churn risk calculation
- Customer value analysis
"""
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Avg

from ..models import Customer, SalesTransaction, Product


class CustomerAnalyzerService:
    """Müşteri analiz ve segmentasyon servisi."""

    # Eşik değerleri
    VIP_SPENDING_THRESHOLD = Decimal('5000')  # Son 6 ayda minimum harcama
    DERMO_VIP_SPENDING_THRESHOLD = Decimal('2000')  # Dermo kategorisinde minimum harcama
    CHURN_DAYS = [30, 60, 90, 120]  # Kayıp riski gün aralıkları

    def update_all_segments(self) -> dict:
        """Tüm müşterilerin segmentlerini güncelle."""
        customers = Customer.objects.all()
        updated = 0

        for customer in customers:
            old_segment = customer.segment
            self._update_customer_segment(customer)
            self._update_churn_risk(customer)

            if customer.segment != old_segment:
                updated += 1

            customer.save()

        return {'updated': updated, 'total': customers.count()}

    def _update_customer_segment(self, customer: Customer):
        """Tek müşteri segmentini güncelle."""
        today = timezone.now().date()
        six_months_ago = today - timedelta(days=180)

        # Son 6 ay satışlarını al
        transactions = SalesTransaction.objects.filter(
            customer=customer,
            sale_date__gte=six_months_ago
        ).select_related('product')

        if not transactions.exists():
            # Hiç alışveriş yoksa
            if customer.last_visit_date and (today - customer.last_visit_date).days > 120:
                customer.segment = 'LOST'
            elif not customer.last_visit_date:
                customer.segment = 'NEW'
            return

        # Toplam ve dermo harcamalarını hesapla
        total_spending = transactions.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        dermo_spending = transactions.filter(
            product__category='DERMO'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

        customer.total_spending = total_spending
        customer.dermo_spending = dermo_spending

        # Son ziyaret tarihini güncelle
        last_transaction = transactions.order_by('-sale_date').first()
        if last_transaction:
            customer.last_visit_date = last_transaction.sale_date

        # Segment belirleme
        if dermo_spending >= self.DERMO_VIP_SPENDING_THRESHOLD:
            customer.segment = 'DERMO_VIP'
        elif total_spending >= self.VIP_SPENDING_THRESHOLD:
            customer.segment = 'VIP'
        elif customer.last_visit_date and (today - customer.last_visit_date).days > 120:
            customer.segment = 'LOST'
        else:
            customer.segment = 'STANDARD'

    def _update_churn_risk(self, customer: Customer):
        """Müşteri kayıp riskini hesapla."""
        if not customer.last_visit_date:
            customer.churn_risk = 100
            return

        today = timezone.now().date()
        days_since_visit = (today - customer.last_visit_date).days

        if days_since_visit <= self.CHURN_DAYS[0]:  # 30 gün
            customer.churn_risk = 0
        elif days_since_visit <= self.CHURN_DAYS[1]:  # 60 gün
            customer.churn_risk = 25
        elif days_since_visit <= self.CHURN_DAYS[2]:  # 90 gün
            customer.churn_risk = 50
        elif days_since_visit <= self.CHURN_DAYS[3]:  # 120 gün
            customer.churn_risk = 75
        else:
            customer.churn_risk = 100

    def get_customer_insights(self, customer: Customer) -> dict:
        """Tek müşteri için detaylı analiz."""
        today = timezone.now().date()
        six_months_ago = today - timedelta(days=180)

        transactions = SalesTransaction.objects.filter(
            customer=customer,
            sale_date__gte=six_months_ago
        ).select_related('product')

        # Ürün kategorisi dağılımı
        category_breakdown = {}
        for tx in transactions:
            cat = tx.product.get_category_display()
            if cat not in category_breakdown:
                category_breakdown[cat] = {'count': 0, 'total': Decimal('0')}
            category_breakdown[cat]['count'] += tx.quantity
            category_breakdown[cat]['total'] += tx.total_amount

        # En çok alınan ürünler
        product_counts = {}
        for tx in transactions:
            pid = tx.product.id
            if pid not in product_counts:
                product_counts[pid] = {
                    'product': tx.product.name,
                    'count': 0,
                    'total': Decimal('0')
                }
            product_counts[pid]['count'] += tx.quantity
            product_counts[pid]['total'] += tx.total_amount

        top_products = sorted(
            product_counts.values(),
            key=lambda x: x['total'],
            reverse=True
        )[:5]

        # Aylık harcama trendi
        monthly_spending = transactions.extra(
            select={'month': "date_trunc('month', sale_date)"}
        ).values('month').annotate(
            total=Sum('total_amount')
        ).order_by('month')

        return {
            'customer_id': customer.id,
            'customer_name': customer.full_name,
            'segment': customer.get_segment_display(),
            'churn_risk': customer.churn_risk,
            'total_spending': float(customer.total_spending),
            'dermo_spending': float(customer.dermo_spending),
            'category_breakdown': category_breakdown,
            'top_products': top_products,
            'transaction_count': transactions.count(),
            'average_transaction': float(transactions.aggregate(
                avg=Avg('total_amount')
            )['avg'] or 0),
            'last_visit': customer.last_visit_date.isoformat() if customer.last_visit_date else None,
        }

    def get_segment_summary(self) -> dict:
        """Segment bazlı özet istatistikler."""
        segments = Customer.objects.values('segment').annotate(
            count=Count('id'),
            total_points=Sum('total_points'),
            avg_churn_risk=Avg('churn_risk')
        )

        return {
            'segments': list(segments),
            'total_customers': Customer.objects.count(),
            'at_risk_count': Customer.objects.filter(churn_risk__gte=50).count(),
            'vip_count': Customer.objects.filter(segment__in=['VIP', 'DERMO_VIP']).count(),
        }
