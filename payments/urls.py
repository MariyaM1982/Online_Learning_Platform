from django.urls import path
from .views import CreateCheckoutSessionView

urlpatterns = [
    path('create-checkout-session/<int:course_id>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
]