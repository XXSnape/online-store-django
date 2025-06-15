from catalog_app.models import Category
from django.db import models


def product_path(instance: "ProductImage", filename: str) -> str:
    """
    Функция определяющая путь до файла.
    :param instance: экземпляр класа ProductImage
    :param filename: имя файла
    :return: путь до файла с изображением товара.
    """
    return "products/images/id_{pk}/{file}".format(
        pk=instance.product.pk, file=filename
    )


class Product(models.Model):
    """
    Модель товара.
    """

    title = models.CharField(
        max_length=128, blank=False, null=False, verbose_name="Название"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    count = models.IntegerField(blank=False, null=False, verbose_name="Количество")
    date = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    description = models.CharField(
        max_length=64, blank=True, null=False, verbose_name="Краткое описание"
    )
    fullDescription = models.TextField(
        blank=True, null=False, verbose_name="Полное описание"
    )
    freeDelivery = models.BooleanField(
        default=False, verbose_name="Бесплатная доставка"
    )
    rating = models.IntegerField(
        blank=False, null=False, verbose_name="Количество звёзд"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("pk",)

    def __str__(self):
        return self.title


class ProductSpecification(models.Model):
    """
    Модель технических характеристик товара.
    """

    name = models.CharField(
        max_length=128, blank=False, null=False, verbose_name="Характеристика"
    )
    value = models.CharField(
        max_length=256, blank=False, null=False, verbose_name="Описание"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="specification",
        verbose_name="Товар",
    )

    class Meta:
        verbose_name = "Техническая характеристика"
        verbose_name_plural = "Технические характеристики"
        ordering = ("pk",)

    def __str__(self):
        return self.name


class SaleProduct(models.Model):
    """
    Модель товара по акции.
    """

    salePrice = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена со скидкой"
    )
    dateFrom = models.DateField(auto_now_add=True, verbose_name="Дата начала акции")
    dateTo = models.DateField(blank=True, verbose_name="Дата окончании акции")
    product: Product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="sale", verbose_name="Товар"
    )

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ("pk",)

    def price(self):
        """
        Метод для сериализатора.
        :return: Возвращает начальную цену товара без скидки.
        """
        return self.product.price

    def title(self):
        """
        Метод для сериализатора.
        :return: Возвращает название товара.
        """
        return self.product.title

    def __str__(self):
        return "{product} теперь стоит {sale}.".format(
            product=self.product.title, sale=self.salePrice
        )


class Tag(models.Model):
    """
    Модель тега.
    """

    name = models.CharField(
        max_length=64, blank=False, null=False, verbose_name="Название"
    )
    product = models.ManyToManyField(Product, related_name="tags", verbose_name="Товар")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("pk",)

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Модель отзыва на товар.
    """

    author = models.CharField(
        max_length=128, blank=False, null=False, verbose_name="Автор"
    )
    email = models.EmailField(
        max_length=64, blank=False, null=False, verbose_name="Email-адрес"
    )
    text = models.TextField(default="", blank=True, null=False, verbose_name="Отзыв")
    rate = models.IntegerField(blank=False, null=False, verbose_name="Оценка")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата написания")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="review", verbose_name="Товар"
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ("pk",)

    def __str__(self):
        return self.author


class ProductImage(models.Model):
    """
    Модель изображения товара.
    """

    image = models.ImageField(
        upload_to=product_path, default="", null=False, verbose_name="Изображение"
    )
    product: Product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_img",
        verbose_name="Товар",
    )

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ("pk",)

    def src(self):
        """
        Метод для сериализатора.
        :return: Возвращает путь до файла
        """
        return "/media/{product_image_path}".format(product_image_path=self.image)

    def alt(self):
        """
        Метод для сериализатора.
        :return: возвращает название товара, связанного с изображением.
        """
        return self.product.title

    def __str__(self):
        return "#{pk} {product}".format(
            pk=self.product.pk,
            product=self.product.title,
        )
