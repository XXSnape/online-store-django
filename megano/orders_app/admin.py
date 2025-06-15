from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Класс для представления заказа в административной панели.
    """

    list_display = (
        "id",
        "user_profile",
        "deliveryType",
        "paymentType",
        "totalCost",
        "status",
        "city",
        "address",
    )
    ordering = ("pk",)
