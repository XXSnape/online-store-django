from django.urls import path

from .views import OrderApiView, OrderDetailApiView, PaymentApiView

app_name = "orders_app"

urlpatterns = [
    path("api/orders", OrderApiView.as_view(), name="orders"),
    path("api/order/<int:pk>", OrderDetailApiView.as_view(), name="order_details"),
    path("api/payment/<int:pk>", PaymentApiView.as_view(), name="payment"),
]
