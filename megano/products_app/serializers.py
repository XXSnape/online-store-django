from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from .models import Tag, Review, Product, SaleProduct
from datetime import datetime


class TagSerializer(serializers.ModelSerializer):
    """
    Класс сериализатор. Основан на модели тегов.
    """

    class Meta:
        model = Tag
        exclude = ("product",)


class ReviewSerializer(serializers.ModelSerializer):
    """
    Класс сериализатор. Основан на модели отзывов.
    """

    class Meta:
        model = Review
        fields = "__all__"


class ProductInfoMixin(serializers.Serializer):
    """
    Миксин с информацией о товаре
    """

    tags = TagSerializer(many=True, required=False)
    images = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    def get_images(self, instance: Product) -> list[dict]:
        """
        Метод сериализатора. Возвращает изображения товара.
        :param instance: экземпляр модели Product
        :return: список из словарей, в которых содержится информация об изображениях товара.
        """
        return [
            {"src": image.src(), "alt": image.alt()}
            for image in instance.product_img.all()
        ]

    def get_price(self, instance: Product):
        """
        Метод сериализатора. Возвращает цену товара.
        :param instance: экземпляр модели Product
        :return: цена товара. Если есть акция на товар, возвращается цена по скидке.
        """
        try:
            return instance.sale.salePrice
        except ObjectDoesNotExist:
            return instance.price


class ProductDetailSerializer(ProductInfoMixin, serializers.ModelSerializer):
    """
    Класс сериализатор. Основан на модели товара. Предоставляет полную информацию о товаре.
    """

    reviews = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "fullDescription",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "specifications",
            "rating",
        )

    def get_reviews(self, instance: Product) -> list[dict]:
        """
        Метод сериализатора. Возвращает отзывы о товаре.
        :param instance: экземпляр модели Product
        :return: список из словарей, в которых содержится информация об отзыве
        """
        return [
            {
                "author": review.author,
                "email": review.email,
                "text": review.text,
                "rate": review.rate,
                "date": datetime.strftime(review.date, "%d-%m-%Y %H:%M"),
            }
            for review in instance.review.all()
        ]

    def get_specifications(self, instance: Product) -> list[dict]:
        """
        Метод сериализатора. Возвращает технические характеристики товара.
        :param instance: экземпляр модели Product
        :return: список из словарей, в которых содержится информация о технических характеристиках.
        """
        return [
            {"name": specification.name, "value": specification.value}
            for specification in instance.specification.all()
        ]


class FewerInfoProductSerializer(ProductInfoMixin, serializers.ModelSerializer):
    """
    Класс сериализатор. Основан на модели товара. Предоставляет неполную информацию о товаре.
    """

    reviews = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
        )

    def get_reviews(self, instance: Product) -> int:
        """
        Метод сериализатора. Возвращает количество отзывов.
        :param instance: экземпляр модели Product
        :return: Количество отзывов.
        """
        return len(instance.review.all())

    def get_price(self, instance: Product):
        """
        Метод сериализатора. Возвращает цену товара.
        :param instance: экземпляр модели Product
        :return: цена товара. Если есть акция на товар, возвращается цена по скидке.
        """
        try:
            return instance.sale.salePrice
        except ObjectDoesNotExist:
            return instance.price


class SaleProductSerializer(serializers.ModelSerializer):
    """
    Класс сериализатор. Основан на модели товаров по акции. Предоставляет информацию об акции.
    """

    id = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    dateFrom = serializers.DateField(format="%d-%m")
    dateTo = serializers.DateField(format="%d-%m")
    price = serializers.StringRelatedField()
    title = serializers.StringRelatedField()

    class Meta:
        model = SaleProduct
        fields = ("id", "price", "salePrice", "dateFrom", "dateTo", "title", "images")

    def get_id(self, instance: SaleProduct) -> Product.pk:
        """
        Метод сериализатора. Возвращает идентификатор товара.
        :param instance: Экземпляр модели SaleProduct
        :return: Идентификатор товара
        """
        return instance.product.pk

    def get_images(self, instance: SaleProduct) -> list[dict]:
        """
        Метод сериализатора. Возвращает изображения товара.
        :param instance: экземпляр модели Product
        :return: список из словарей, в которых содержится информация об изображениях товара.
        """
        return [
            {"src": image.src(), "alt": image.alt()}
            for image in instance.product.product_img.all()
        ]
