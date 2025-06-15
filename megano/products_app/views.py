from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from .models import Tag, Product, SaleProduct
from django.db.models import Count
from .serializers import (
    TagSerializer,
    ReviewSerializer,
    ProductDetailSerializer,
    SaleProductSerializer,
    FewerInfoProductSerializer,
)

from profileuser_app.models import ProfileUser
from .utils import (
    setup_average_rating,
    get_valid_review_data,
    create_review,
    user_review_exists,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class TagsListApiView(ListAPIView):
    """Класс API-view. Предоставляет информацию о тегах."""

    queryset = Tag.objects.only("pk", "name").all()
    serializer_class = TagSerializer

    def get(self, request: Request, *args, **kwargs):
        """Метод - get. Формирует ответ для пользователя"""
        print("backs", list(self.filter_backends))
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductDetailApiView(RetrieveAPIView):
    """Класс API-view. Предоставляет информацию о товаре."""

    queryset = (
        Product.objects.prefetch_related(
            "review", "specification", "product_img", "tags"
        )
        .select_related("category")
        .all()
    )
    serializer_class = ProductDetailSerializer


class SaleListApiView(ListAPIView):
    """Класс API-view. Предоставляет информацию о товарах по акции."""

    queryset: SaleProduct = SaleProduct.objects.prefetch_related("product").all()
    serializer_class = SaleProductSerializer

    def list(self, request: Request, *args, **kwargs):
        """Переопределение метода list для вывода в нужном формате."""
        response = super().list(request, *args, **kwargs)
        response.data["items"] = response.data.pop("results")
        return response


class ProductLimitedListApiView(ListAPIView):
    """Класс API-view. Предоставляет информацию об ограниченных товарах."""

    queryset: Product = (
        Product.objects.prefetch_related("review", "product_img", "tags")
        .select_related("category")
        .filter(count=0)[:16]
    )
    serializer_class = FewerInfoProductSerializer

    def get(self, request: Request, *args, **kwargs):
        """Метод - get. Формирует ответ для пользователя"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductPopularListApiView(ListAPIView):
    """Класс API-view. Предоставляет информацию о самых популярных товарах."""

    queryset: Product = (
        Product.objects.prefetch_related("review", "product_img", "tags")
        .select_related("category")
        .annotate(quantity_purchases=Count("review"))
        .order_by("-quantity_purchases")
        .exclude(count=0)[:8]
    )
    serializer_class = FewerInfoProductSerializer

    def get(self, request, *args, **kwargs):
        """Метод - get. Формирует ответ для пользователя"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CreateProductReviewApiView(CreateAPIView):
    """Класс API-view. Предоставляет возможность пользователю оставить отзыв о товаре."""

    queryset = Product.objects.only("pk", "rating").prefetch_related("review")

    serializer_class = ReviewSerializer
    lookup_url_kwarg = "pk"
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Метод - post. Обрабатывает пользовательские данные и создает новый отзыв.
        Пользователь сможет оставить отзыв, только если установил свой уникальный email в профиле.
        :param request: запрос
        :param args: позиционные аргументы
        :param kwargs: именованные аргументы
        :return: статус 201, если отзыв был создан.
        """
        user: ProfileUser = ProfileUser.objects.get(id=request.user.pk)
        product: Product = self.get_object()

        valid_review_data = get_valid_review_data(
            request_data=request.data, user=user, product=product
        )
        user_review_exists(
            email=valid_review_data.get("email"),
            product_id=valid_review_data.get("product"),
        )

        review_serializer: ReviewSerializer = self.get_serializer(
            data=valid_review_data
        )
        review_serializer.is_valid(raise_exception=True)
        create_review(valid_data=valid_review_data, product=product)

        product.rating = setup_average_rating(product_pk=product.pk)
        product.save()
        return Response(status=status.HTTP_201_CREATED)
