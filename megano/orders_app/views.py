from basket_app.basket import Basket
from products_app.models import Product
from profileuser_app.models import ProfileUser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderSerializer
from .utils import (
    check_delivery_type_and_price_setting,
    get_detail_order_data,
    get_detail_payment_data,
    get_order_user_or_400,
    remove_goods_from_warehouse,
    save_number_products_in_basket,
    setup_count_products_in_basket,
    setup_order,
    validation_all_data,
)


class OrderApiView(APIView):
    """
    Класс API - view. Предоставляет возможность получить историю заказов и создать новый.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        return Response(
            OrderSerializer(
                Order.objects.filter(user_profile=request.user.pk), many=True
            ).data
        )

    def post(self, request: Request):
        bk = Basket(request)

        products = (
            Product.objects.prefetch_related("review", "product_img", "tags")
            .select_related("category")
            .filter(id__in=[product.get("id", 0) for product in request.data])
        )

        order = Order.objects.create(
            user_profile=ProfileUser.objects.get(id=request.user.pk),
            totalCost=bk.get_total_price(),
            status="unconfirmed",
        )

        order.products.set(products)
        order.save()
        save_number_products_in_basket(order_pk=order.pk, products=products, bk=bk)
        return Response(dict(orderId=order.pk))


class OrderDetailApiView(APIView):
    """
    Класс API - view.
    Предоставляет возможность получить детальную информацию о заказе и дополнить информацией существующий.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk: Order.pk):
        order = get_order_user_or_400(request=request, pk=pk)
        serialized_data = OrderSerializer(order, many=False).data
        setup_count_products_in_basket(order_pk=order.pk, data=serialized_data)
        return Response(serialized_data)

    def post(self, request: Request, pk: Order.pk):
        order = get_order_user_or_400(request=request, pk=pk)
        setup_order(order=order, params=get_detail_order_data(order_data=request.data))
        check_delivery_type_and_price_setting(order=order)
        order.save()
        return Response(OrderSerializer(order, many=False).data)


class PaymentApiView(APIView):
    """
    Класс API - view. Предоставляет возможность оплатить заказ.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, pk: Order.pk) -> Response:
        order = get_order_user_or_400(request=request, pk=pk, payment=True)
        bk = Basket(request)
        number_card, name, month, year, code = get_detail_payment_data(request.data)
        validation_all_data(
            name=name, number="54789342", month=month, year=year, code=code
        )
        order.status = "accepted"
        remove_goods_from_warehouse(order=order, bk=bk)
        order.save()
        bk.clear()
        return Response(status=status.HTTP_200_OK)
