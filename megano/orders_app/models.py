from django.db import models
from products_app.models import Product
from profileuser_app.models import ProfileUser


class Order(models.Model):
    """
    Модель заказа.
    """

    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    user_profile: ProfileUser = models.ForeignKey(
        ProfileUser,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Пользователь",
    )
    deliveryType = models.CharField(
        max_length=32, blank=True, null=False, verbose_name="Тип доставки"
    )
    paymentType = models.CharField(
        max_length=32, blank=True, null=False, verbose_name="Тип оплаты"
    )
    totalCost = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена заказа"
    )
    status = models.CharField(
        max_length=32, blank=True, null=False, verbose_name="Статус оплаты"
    )
    city = models.CharField(max_length=64, blank=True, null=False, verbose_name="Город")
    address = models.CharField(
        max_length=128, blank=True, null=False, verbose_name="Адрес"
    )
    products = models.ManyToManyField(
        Product, related_name="orders", verbose_name="Товары"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ("pk",)

    def fullName(self) -> str:
        """
        Получает имя пользователя
        :return: Имя пользователя, оформившего заказ.
        """
        return self.user_profile.fullName

    def email(self) -> str:
        """
        Получает email пользователя
        :return: Email пользователя, оформившего заказ.
        """
        return self.user_profile.email

    def phone(self) -> str:
        """
        Получает номер телефона пользователя
        :return: Номер телефона пользователя, оформившего заказ.
        """
        return self.user_profile.phone

    def __str__(self):
        return "Пользователь {user}, заказ #{pk}.".format(
            user=self.user_profile.fullName, pk=self.pk
        )


class QuantityProductsInBasket(models.Model):
    """
    Модель, сохраняющая количество товара в корзине при оформлении заказа.
    """

    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(blank=False)
