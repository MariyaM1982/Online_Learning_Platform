from django.urls import path
from .views import UserProfileView, PaymentListAPIView, UserRegisterView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
]