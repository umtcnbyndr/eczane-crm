"""
Management command to update customer segments.
Run after data import or periodically.
"""
from django.core.management.base import BaseCommand
from core.services.customer_analyzer import CustomerAnalyzerService


class Command(BaseCommand):
    help = 'Müşteri segmentlerini ve kayıp risklerini güncelle'

    def handle(self, *args, **options):
        analyzer = CustomerAnalyzerService()

        self.stdout.write('Müşteri segmentleri güncelleniyor...')

        result = analyzer.update_all_segments()

        self.stdout.write(self.style.SUCCESS(
            f"Toplam {result['total']} müşteri işlendi, {result['updated']} segment güncellendi"
        ))

        # Özet istatistikleri göster
        summary = analyzer.get_segment_summary()
        self.stdout.write('\nSegment Dağılımı:')
        for seg in summary['segments']:
            self.stdout.write(f"  - {seg['segment']}: {seg['count']} müşteri")

        self.stdout.write(f"\nRisk altındaki müşteri: {summary['at_risk_count']}")
        self.stdout.write(f"VIP müşteri: {summary['vip_count']}")
