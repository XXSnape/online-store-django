from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from products_app.models import Product
from products_app.serializers import FewerInfoProductSerializer
from .models import Category
from .serializers import CategorySerializer
from .utils import main_filter


class CategoryListApiView(ListAPIView):
    """Класс API-view. Предоставляет информацию о категориях."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        """Метод - get. Формирует ответ для пользователя"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BannersListApiView(ListAPIView):
    """Класс API-view. Предоставляет информацию о товарах в избранных категориях."""

    queryset: Product = (
        Product.objects.prefetch_related(
            "review",
            "product_img",
            "tags",
        )
        .select_related("category")
        .filter(category__main=True)
    )
    serializer_class = FewerInfoProductSerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        """Метод - get. Формирует ответ для пользователя"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CatalogApiView(APIView):
    """Класс API-view. Позволяет отфильтровать товары."""

    def get(self, request: Request) -> Response:
        """Метод - get. Формирует ответ для пользователя"""
        return Response(
            {"items": FewerInfoProductSerializer(main_filter(request), many=True).data}
        )
