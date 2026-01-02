"""
Admin configuration for SmartPharmacy CRM.
"""
from django.contrib import admin
from .models import Customer, Product, SalesTransaction, Staff, Task, ExcelUpload, Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_premium', 'product_count', 'created_at']
    list_filter = ['category', 'is_premium']
    search_fields = ['name']
    ordering = ['-product_count']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_code', 'full_name', 'phone', 'segment', 'total_points', 'churn_risk', 'last_visit_date']
    list_filter = ['segment', 'churn_risk']
    search_fields = ['first_name', 'last_name', 'phone', 'customer_code']
    ordering = ['-total_points']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['barcode', 'name', 'category', 'stock_quantity', 'unit_price', 'usage_duration']
    list_filter = ['category']
    search_fields = ['barcode', 'name', 'brand']


@admin.register(SalesTransaction)
class SalesTransactionAdmin(admin.ModelAdmin):
    list_display = ['sale_date', 'customer', 'product', 'quantity', 'total_amount']
    list_filter = ['sale_date']
    search_fields = ['customer__first_name', 'customer__last_name', 'product__name']
    date_hierarchy = 'sale_date'


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_points', 'weekly_points', 'tasks_completed']
    ordering = ['-total_points']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_type', 'customer', 'status', 'priority', 'assigned_to', 'due_date']
    list_filter = ['status', 'task_type', 'priority']
    search_fields = ['title', 'customer__first_name', 'customer__last_name']
    date_hierarchy = 'due_date'


@admin.register(ExcelUpload)
class ExcelUploadAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'file_type', 'status', 'rows_processed', 'created_at']
    list_filter = ['status', 'file_type']
    readonly_fields = ['rows_processed', 'rows_failed', 'error_message', 'processed_at']
