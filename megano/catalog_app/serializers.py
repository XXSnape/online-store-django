from rest_framework import serializers
from .models import Category


class CategoryImageMixin(serializers.Serializer):
    """
    Миксин с картинкой категории
    """

    image = serializers.SerializerMethodField()

    def get_image(self, instance: Category) -> dict[str, str] | dict:
        """
        Метод сериализатора. Возвращает изображение категории.
        :param instance: экземпляр модели Category
        :return: словарь, в котором содержится информация об изображении категории.
        """
        try:
            image = instance.category_img.all()[0]
            return {"src": image.src(), "alt": image.alt()}
        except IndexError:
            return {}


class SubCategorySerializer(CategoryImageMixin, serializers.ModelSerializer):
    """
    Класс сериализатор. Основан на модели категории.
    """

    class Meta:
        model = Category
        fields = ("id", "title", "image")


class CategorySerializer(CategoryImageMixin, serializers.ModelSerializer):
    """
    Класс сериализатор. Основан на модели категории.
    """

    subcategories = SubCategorySerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Category
        fields = ("id", "title", "image", "subcategories")
