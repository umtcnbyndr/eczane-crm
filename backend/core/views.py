"""
API Views for SmartPharmacy CRM.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import timedelta

from .models import Customer, Product, SalesTransaction, Staff, Task, ExcelUpload, Brand
from .serializers import (
    CustomerSerializer, CustomerListSerializer, ProductSerializer,
    SalesTransactionSerializer, StaffSerializer, TaskSerializer,
    TaskCreateSerializer, TaskCompleteSerializer, ExcelUploadSerializer,
    DashboardStatsSerializer, LeaderboardSerializer, BrandSerializer
)
from .services.excel_parser import ExcelParserService


class BrandViewSet(viewsets.ModelViewSet):
    """Marka API."""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    def get_queryset(self):
        queryset = Brand.objects.annotate(
            actual_product_count=Count('products')
        ).order_by('-actual_product_count')

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        return queryset


class CustomerViewSet(viewsets.ModelViewSet):
    """Müşteri API."""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer

    def get_queryset(self):
        queryset = Customer.objects.all()
        segment = self.request.query_params.get('segment')
        churn_risk_min = self.request.query_params.get('churn_risk_min')
        search = self.request.query_params.get('search')

        if segment:
            queryset = queryset.filter(segment=segment)
        if churn_risk_min:
            queryset = queryset.filter(churn_risk__gte=int(churn_risk_min))
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone__icontains=search)
            )
        return queryset

    @action(detail=False, methods=['get'])
    def at_risk(self, request):
        """Kayıp riski yüksek müşteriler."""
        customers = self.get_queryset().filter(churn_risk__gte=50).order_by('-churn_risk')[:20]
        serializer = CustomerListSerializer(customers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def vip(self, request):
        """VIP müşteriler."""
        customers = self.get_queryset().filter(segment__in=['VIP', 'DERMO_VIP']).order_by('-total_points')
        serializer = CustomerListSerializer(customers, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """Ürün API."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        low_stock = self.request.query_params.get('low_stock')

        if category:
            queryset = queryset.filter(category=category)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(barcode__icontains=search) |
                Q(brand__icontains=search)
            )
        if low_stock:
            queryset = queryset.filter(stock_quantity__lte=10)
        return queryset


class SalesTransactionViewSet(viewsets.ModelViewSet):
    """Satış İşlemi API."""
    queryset = SalesTransaction.objects.select_related('customer', 'product').all()
    serializer_class = SalesTransactionSerializer

    def get_queryset(self):
        queryset = SalesTransaction.objects.select_related('customer', 'product').all()
        customer_id = self.request.query_params.get('customer')
        product_id = self.request.query_params.get('product')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if date_from:
            queryset = queryset.filter(sale_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(sale_date__lte=date_to)
        return queryset


class StaffViewSet(viewsets.ModelViewSet):
    """Personel API."""
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Haftalık liderlik tablosu."""
        period = request.query_params.get('period', 'weekly')

        if period == 'weekly':
            staff_list = Staff.objects.order_by('-weekly_points')[:10]
        elif period == 'monthly':
            staff_list = Staff.objects.order_by('-monthly_points')[:10]
        else:
            staff_list = Staff.objects.order_by('-total_points')[:10]

        data = []
        for rank, staff in enumerate(staff_list, 1):
            data.append({
                'id': staff.id,
                'name': staff.name,
                'total_points': staff.total_points,
                'weekly_points': staff.weekly_points,
                'tasks_completed': staff.tasks_completed,
                'rank': rank
            })
        return Response(data)

    @action(detail=True, methods=['post'])
    def reset_weekly(self, request, pk=None):
        """Haftalık puanları sıfırla."""
        Staff.objects.all().update(weekly_points=0)
        return Response({'status': 'weekly points reset'})


class TaskViewSet(viewsets.ModelViewSet):
    """Görev API."""
    queryset = Task.objects.select_related('customer', 'product', 'assigned_to').all()
    serializer_class = TaskSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.select_related('customer', 'product', 'assigned_to').all()
        status_filter = self.request.query_params.get('status')
        task_type = self.request.query_params.get('type')
        assigned_to = self.request.query_params.get('assigned_to')
        today_only = self.request.query_params.get('today')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if task_type:
            queryset = queryset.filter(task_type=task_type)
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        if today_only:
            today = timezone.now().date()
            queryset = queryset.filter(
                Q(due_date=today) | Q(due_date__isnull=True, status='PENDING')
            )
        return queryset

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Bugünün görevleri."""
        today = timezone.now().date()
        tasks = self.get_queryset().filter(
            Q(due_date=today) | Q(due_date__lt=today, status='PENDING')
        ).filter(status__in=['PENDING', 'IN_PROGRESS'])
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Görevi tamamla."""
        task = self.get_object()
        serializer = TaskCompleteSerializer(data=request.data)

        if serializer.is_valid():
            task.status = serializer.validated_data.get('status', 'COMPLETED')
            task.notes = serializer.validated_data.get('notes', '')
            task.completed_at = timezone.now()
            task.save()

            # Personele puan ekle
            if task.assigned_to and task.status == 'COMPLETED':
                task.assigned_to.add_points(task.points_value)
                task.assigned_to.tasks_completed += 1
                task.assigned_to.save()

            return Response(TaskSerializer(task).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Görevi personele ata."""
        task = self.get_object()
        staff_id = request.data.get('staff_id')

        try:
            staff = Staff.objects.get(id=staff_id)
            task.assigned_to = staff
            task.save()
            return Response(TaskSerializer(task).data)
        except Staff.DoesNotExist:
            return Response({'error': 'Personel bulunamadı'}, status=status.HTTP_404_NOT_FOUND)


class ExcelUploadView(APIView):
    """Excel dosya yükleme API."""
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file = request.FILES.get('file')
        file_type = request.data.get('file_type')

        if not file:
            return Response({'error': 'Dosya gerekli'}, status=status.HTTP_400_BAD_REQUEST)

        if not file_type:
            return Response({'error': 'Dosya tipi gerekli'}, status=status.HTTP_400_BAD_REQUEST)

        # Excel kaydı oluştur
        excel_upload = ExcelUpload.objects.create(
            file=file,
            file_type=file_type,
            file_name=file.name,
            status='PROCESSING'
        )

        try:
            # Excel'i işle
            parser = ExcelParserService()
            result = parser.process_file(excel_upload)

            excel_upload.status = 'COMPLETED'
            excel_upload.rows_processed = result.get('rows_processed', 0)
            excel_upload.rows_failed = result.get('rows_failed', 0)
            excel_upload.processed_at = timezone.now()
            excel_upload.save()

            # Include debug info in response
            response_data = ExcelUploadSerializer(excel_upload).data
            response_data['debug'] = {
                'total_rows': result.get('debug_total_rows', 0),
                'customer_rows': result.get('debug_customer_rows', 0),
                'header_rows': result.get('debug_header_rows', 0),
                'product_rows': result.get('debug_product_rows', 0),
                'transactions_created': result.get('transactions_created', 0),
                'products_created': result.get('products_created', 0),
                'customers_created': result.get('customers_created', 0),
            }
            return Response(response_data)

        except Exception as e:
            excel_upload.status = 'FAILED'
            excel_upload.error_message = str(e)
            excel_upload.save()
            return Response({
                'error': str(e),
                'upload': ExcelUploadSerializer(excel_upload).data
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExcelUploadListView(APIView):
    """Excel yükleme geçmişi."""

    def get(self, request):
        uploads = ExcelUpload.objects.all()[:20]
        serializer = ExcelUploadSerializer(uploads, many=True)
        return Response(serializer.data)


class ResetDataView(APIView):
    """Tüm verileri sil - TEST İÇİN."""

    def post(self, request):
        # Silme işlemi
        transactions_count = SalesTransaction.objects.count()
        SalesTransaction.objects.all().delete()

        products_count = Product.objects.count()
        Product.objects.all().delete()

        brands_count = Brand.objects.count()
        Brand.objects.all().delete()

        customers_count = Customer.objects.count()
        Customer.objects.all().delete()

        uploads_count = ExcelUpload.objects.count()
        ExcelUpload.objects.all().delete()

        # Görevleri de sil
        tasks_count = Task.objects.count()
        Task.objects.all().delete()

        return Response({
            'message': 'Tüm veriler silindi',
            'deleted': {
                'transactions': transactions_count,
                'products': products_count,
                'brands': brands_count,
                'customers': customers_count,
                'uploads': uploads_count,
                'tasks': tasks_count,
            }
        })


class DashboardView(APIView):
    """Dashboard istatistikleri."""

    def get(self, request):
        today = timezone.now().date()

        stats = {
            'total_customers': Customer.objects.count(),
            'vip_customers': Customer.objects.filter(segment__in=['VIP', 'DERMO_VIP']).count(),
            'lost_customers': Customer.objects.filter(segment='LOST').count(),
            'at_risk_customers': Customer.objects.filter(churn_risk__gte=50).count(),
            'pending_tasks': Task.objects.filter(status='PENDING').count(),
            'today_tasks': Task.objects.filter(
                Q(due_date=today) | Q(due_date__lt=today, status='PENDING')
            ).filter(status__in=['PENDING', 'IN_PROGRESS']).count(),
            'completed_tasks_today': Task.objects.filter(
                completed_at__date=today,
                status='COMPLETED'
            ).count(),
            'total_points_today': Task.objects.filter(
                completed_at__date=today,
                status='COMPLETED'
            ).aggregate(total=Sum('points_value'))['total'] or 0,
            'total_products': Product.objects.count(),
            'low_stock_products': Product.objects.filter(stock_quantity__lte=10).count(),
        }

        return Response(stats)


@api_view(['POST'])
def generate_replenishment_tasks(request):
    """Ürün bitiş hatırlatma görevlerini oluştur."""
    from .services.task_generator import TaskGeneratorService

    generator = TaskGeneratorService()
    result = generator.generate_replenishment_tasks()

    return Response({
        'message': 'Görevler oluşturuldu',
        'tasks_created': result.get('created', 0)
    })


@api_view(['POST'])
def update_customer_segments(request):
    """Müşteri segmentlerini güncelle."""
    from .services.customer_analyzer import CustomerAnalyzerService

    analyzer = CustomerAnalyzerService()
    result = analyzer.update_all_segments()

    return Response({
        'message': 'Segmentler güncellendi',
        'customers_updated': result.get('updated', 0)
    })
