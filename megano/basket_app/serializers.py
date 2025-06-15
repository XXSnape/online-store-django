from rest_framework import serializers
from products_app.models import Product
from products_app.serializers import TagSerializer


class BasketSerializer(serializers.ModelSerializer):
    """
    Сериализатор корзины.
    """

    tags = TagSerializer(many=True, required=False)
    reviews = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
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

    def get_count(self, instance: Product) -> int:
        """
        Возвращает количество товара в корзине
        :param instance: экземпляр модели Product
        :return: Количество товара
        """
        return self.context.get_count_product_in_basket(product_pk=instance.pk)

    def get_price(self, instance: Product) -> int:
        """
        Возвращает цену товара в корзине
        :param instance: экземпляр модели Product
        :return: Цена товара
        """
        return self.context.get_price_product_in_basket(product_pk=instance.pk)

    def get_reviews(self, instance: Product) -> int:
        """
        Метод сериализатора. Возвращает количество отзывов.
        :param instance: экземпляр модели Product
        :return: Количество отзывов.
        """
        return len(instance.review.all())

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
