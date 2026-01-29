from django.urls import path
from .views import venue_dashboard

urlpatterns = [
    path('', venue_dashboard, name='venue_dashboard')
]