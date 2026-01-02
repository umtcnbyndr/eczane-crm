"""
Management command to generate automatic tasks.
Run daily via cron or scheduler.
"""
from django.core.management.base import BaseCommand
from core.services.task_generator import TaskGeneratorService


class Command(BaseCommand):
    help = 'Otomatik görevleri oluştur (hatırlatma, VIP takip, kayıp önleme)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['all', 'replenishment', 'churn', 'vip', 'seasonal'],
            default='all',
            help='Oluşturulacak görev tipi'
        )

    def handle(self, *args, **options):
        generator = TaskGeneratorService()
        task_type = options['type']

        self.stdout.write('Görevler oluşturuluyor...')

        if task_type == 'all':
            result = generator.generate_all_tasks()
            self.stdout.write(self.style.SUCCESS(
                f"Toplam {result['total_created']} görev oluşturuldu"
            ))
            for name, detail in result['details'].items():
                self.stdout.write(f"  - {name}: {detail.get('created', 0)} görev")

        elif task_type == 'replenishment':
            result = generator.generate_replenishment_tasks()
            self.stdout.write(self.style.SUCCESS(
                f"{result['created']} ürün hatırlatma görevi oluşturuldu"
            ))

        elif task_type == 'churn':
            result = generator.generate_churn_prevention_tasks()
            self.stdout.write(self.style.SUCCESS(
                f"{result['created']} kayıp önleme görevi oluşturuldu"
            ))

        elif task_type == 'vip':
            result = generator.generate_vip_followup_tasks()
            self.stdout.write(self.style.SUCCESS(
                f"{result['created']} VIP takip görevi oluşturuldu"
            ))

        elif task_type == 'seasonal':
            result = generator.generate_seasonal_dermo_tasks()
            self.stdout.write(self.style.SUCCESS(
                f"{result['created']} mevsimsel dermo görevi oluşturuldu"
            ))
