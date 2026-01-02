"""
URL configuration for core app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CustomerViewSet, ProductViewSet, SalesTransactionViewSet,
    StaffViewSet, TaskViewSet, ExcelUploadView, ExcelUploadListView,
    DashboardView, generate_replenishment_tasks, update_customer_segments
)

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'products', ProductViewSet)
router.register(r'sales', SalesTransactionViewSet)
router.register(r'staff', StaffViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('upload/', ExcelUploadView.as_view(), name='excel-upload'),
    path('uploads/', ExcelUploadListView.as_view(), name='excel-upload-list'),
    path('generate-tasks/', generate_replenishment_tasks, name='generate-tasks'),
    path('update-segments/', update_customer_segments, name='update-segments'),
]
