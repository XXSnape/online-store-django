from products_app.models import Product
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .basket import Basket
from .utils import check_user_input_count, get_serialized_data


class BasketApiView(APIView):
    """
    Класс - API-view. Позволяет получить информацию о корзине, добавить в нее товар или удалить его.
    """

    def get(self, request: Request) -> Response:
        return Response(get_serialized_data(basket=Basket(request)))

    def post(self, request: Request) -> Response:
        bk = Basket(request)
        product = get_object_or_404(Product, id=request.data.get("id", 0))
        bk.add(
            product, count=check_user_input_count(request.data, product=product, bk=bk)
        )
        return Response(get_serialized_data(basket=bk))

    def delete(self, request: Request) -> Response:
        bk = Basket(request)
        bk.delete(
            get_object_or_404(Product, id=request.data.get("id", 0)),
            request.data.get("count", 0),
        )
        return Response(get_serialized_data(basket=bk))
