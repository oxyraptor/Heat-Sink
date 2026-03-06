"""
URL configuration for fins_api.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HeatSinkViewSet, StatusView, MaterialsView

# Create router for ViewSet
router = DefaultRouter()
router.register(r'api', HeatSinkViewSet, basename='heatsink')

urlpatterns = [
    # Root status endpoint
    path('', StatusView.as_view(), name='status'),
    
    # Materials endpoint
    path('materials/', MaterialsView.as_view(), name='materials'),
    
    # Recommendation endpoint
    path('recommend/', HeatSinkViewSet.as_view({'post': 'recommend'}), name='recommend'),
    
    # ML prediction endpoint
    path('predict-ml/', HeatSinkViewSet.as_view({'post': 'predict_ml'}), name='predict-ml'),
    
    # Include router URLs (alternative approach)
    # path('', include(router.urls)),
]
