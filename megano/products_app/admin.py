from django.contrib import admin

from .models import (
    Product,
    ProductImage,
    ProductSpecification,
    Review,
    SaleProduct,
    Tag,
)


class ProductSpecificationInline(admin.StackedInline):
    """
    Класс для связи товара с его техническими характеристиками в административной панели.
    """

    model = ProductSpecification


class TagInline(admin.StackedInline):
    """
    Класс для связи товара с его тегами в административной панели.
    """

    model = Product.tags.through


class ProductImageInline(admin.StackedInline):
    """
    Класс для связи товара с его изображениями в административной панели.
    """

    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Класс для представления товара в административной панели.
    """

    inlines = [
        ProductSpecificationInline,
        TagInline,
        ProductImageInline,
    ]

    list_display = (
        "pk",
        "title",
        "price",
        "count",
        "date",
        "description",
        "fullDescription",
        "freeDelivery",
        "rating",
        "category",
    )

    list_editable = ("freeDelivery",)

    list_display_links = ("pk", "title")
    ordering = ("pk",)

    def description_short(self, obj: Product) -> str:
        """
        Метод - валидатор
        :param obj: объект класса Product
        :return: возвращает укороченное полное описание в административную панель.
        """
        if len(obj.fullDescription) < 50:
            return obj.fullDescription
        return obj.fullDescription[:50] + "..."


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Класс для представления тегов в административной панели.
    """

    list_display = ("pk", "name")
    list_display_links = ("pk", "name")
    ordering = ("pk",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Класс для представления отзывов в административной панели.
    """

    list_display = ("pk", "author", "email", "text", "rate", "date", "product")
    list_display_links = ("pk", "author")
    ordering = ("pk",)


@admin.register(SaleProduct)
class SaleProductAdmin(admin.ModelAdmin):
    """
    Класс для представления товаров по акции в административной панели.
    """

    list_display = ("pk", "salePrice", "dateFrom", "dateTo", "product")
    list_display_links = ("pk",)
    ordering = ("pk",)


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    """
    Класс для представления технических характеристик товара.
    """

    list_display = ("pk", "name", "value", "product")
    list_display_links = ("pk", "name")
    ordering = ("pk",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Класс для предоставления изображений товара.
    """

    list_display = ("pk", "image", "product")
    list_display_links = ("pk",)
    ordering = ("pk",)
