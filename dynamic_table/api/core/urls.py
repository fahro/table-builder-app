from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DynamicTableViewSet,
    DynamicTableRowCreateViewSet,
    DynamicTableRowListViewSet
)

table_router = DefaultRouter()
table_router.register('', DynamicTableViewSet, basename='dynamic-table')

row_router = DefaultRouter()
row_router.register('row', DynamicTableRowCreateViewSet, basename='dynamic-table-row')
row_router.register('rows', DynamicTableRowListViewSet, basename='dynamic-table-rows')

urlpatterns = [
    path('', include(table_router.urls)),
    path('<int:id>/', include(row_router.urls)),
]
