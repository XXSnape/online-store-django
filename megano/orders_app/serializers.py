from rest_framework import serializers
from products_app.serializers import FewerInfoProductSerializer
from .models import Order
from .utils import get_nice_data


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор заказа.
    """

    createdAt = serializers.SerializerMethodField()
    orderId = serializers.SerializerMethodField()
    fullName = serializers.StringRelatedField()
    email = serializers.StringRelatedField()
    phone = serializers.StringRelatedField()
    products = FewerInfoProductSerializer(many=True, required=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
            "orderId",
        )

    def get_createdAt(self, instance: Order) -> str:
        """
        Метод - сериалзатора. Возвращает дату создания заказа.
        :param instance: Экземпляр модели Order
        :return: Дата создания заказа в нужном формате
        """
        return get_nice_data(date=instance.createdAt)

    def get_orderId(self, instance: Order) -> Order.pk:
        return instance.pk
