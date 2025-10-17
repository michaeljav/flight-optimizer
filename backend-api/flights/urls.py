# flights/urls.py
from django.urls import path
from .views import best_value

urlpatterns = [
    path("best", best_value),  # endpoint: /api/best
]
