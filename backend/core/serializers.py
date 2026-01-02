"""
Serializers for SmartPharmacy CRM API.
"""
from rest_framework import serializers
from .models import Customer, Product, SalesTransaction, Staff, Task, ExcelUpload, Brand


class BrandSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'category', 'category_display', 'is_premium', 'product_count', 'created_at']


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    segment_display = serializers.CharField(source='get_segment_display', read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'customer_code', 'first_name', 'last_name', 'full_name',
            'phone', 'phone_secondary', 'total_points', 'points_tl_value',
            'segment', 'segment_display', 'churn_risk', 'last_visit_date',
            'total_spending', 'dermo_spending', 'created_at', 'updated_at'
        ]


class CustomerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'customer_code', 'full_name', 'phone', 'segment', 'total_points', 'churn_risk']


class ProductSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, default='')

    class Meta:
        model = Product
        fields = [
            'id', 'barcode', 'product_code', 'name', 'brand', 'brand_name',
            'category', 'category_display', 'kdv_rate',
            'stock_quantity', 'unit_price', 'usage_duration',
            'created_at', 'updated_at'
        ]


class SalesTransactionSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = SalesTransaction
        fields = [
            'id', 'customer', 'customer_name', 'product', 'product_name',
            'sale_date', 'quantity', 'unit_price', 'total_amount', 'kdv_amount',
            'created_at'
        ]


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = [
            'id', 'name', 'total_points', 'weekly_points', 'monthly_points',
            'tasks_completed', 'created_at', 'updated_at'
        ]


class TaskSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.name', read_only=True)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'task_type', 'task_type_display', 'customer', 'customer_name',
            'customer_phone', 'product', 'product_name', 'title', 'description',
            'status', 'status_display', 'priority', 'priority_display',
            'points_value', 'assigned_to', 'assigned_to_name', 'due_date',
            'completed_at', 'notes', 'created_at', 'updated_at'
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'task_type', 'customer', 'product', 'title', 'description',
            'priority', 'points_value', 'assigned_to', 'due_date'
        ]


class TaskCompleteSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=['COMPLETED', 'UNREACHABLE'], default='COMPLETED')


class ExcelUploadSerializer(serializers.ModelSerializer):
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ExcelUpload
        fields = [
            'id', 'file', 'file_type', 'file_type_display', 'file_name',
            'status', 'status_display', 'rows_processed', 'rows_failed',
            'error_message', 'created_at', 'processed_at'
        ]
        read_only_fields = ['file_name', 'status', 'rows_processed', 'rows_failed', 'error_message', 'processed_at']


class DashboardStatsSerializer(serializers.Serializer):
    """Dashboard istatistikleri."""
    total_customers = serializers.IntegerField()
    vip_customers = serializers.IntegerField()
    lost_customers = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    completed_tasks_today = serializers.IntegerField()
    total_points_today = serializers.IntegerField()


class LeaderboardSerializer(serializers.Serializer):
    """Liderlik tablosu."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    total_points = serializers.IntegerField()
    weekly_points = serializers.IntegerField()
    tasks_completed = serializers.IntegerField()
    rank = serializers.IntegerField()
