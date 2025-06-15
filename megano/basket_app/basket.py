from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist

from megano import settings
from products_app.models import Product
from rest_framework.request import Request


class Basket:
    """Корзина для товаров."""

    def __init__(self, request: Request):
        """
        Инициализация корзины. Установка сессии.
        Сама корзина представляет собой словарь, где ключ - это идентификатор товара.
        Значение - словарь, состоящий из цены и количества товара в корзине
        :param request: запрос
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = dict()
        self.cart = cart

    def add(self, product: Product, count: int = 1):
        """
        Метод добавления товара в корзину. Если на товар есть акция, то берется цена по скидке.
        :param product: Товар
        :param count: Количество товара
        :return: Сохраняет товар в корзину.
        """
        product_id = str(product.pk)
        try:
            price = product.sale.salePrice
        except ObjectDoesNotExist:
            price = product.price
        if product_id not in self.cart:
            self.cart[product_id] = {
                "count": count,
                "price": str(price),
            }
        else:
            self.cart[product_id]["count"] += count
        self.save()

    def delete(self, product: Product, count: int = 1):
        """
        Метод удаления товара из корзины.
        :param product: Товар
        :param count: Количество удаляемых товаров
        :return: Удаляет товар из корзины.
        """
        product_id = str(product.pk)
        if count >= self.cart[product_id]["count"]:
            del self.cart[product_id]
        else:
            self.cart[product_id]["count"] -= count

        self.save()

    def save(self):
        """
        Метод сохранения изменений в корзине.
        """
        self.session.modified = True

    def clear(self):
        """
        Метод полной очистки корзины.
        """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def get_total_price(self) -> Decimal:
        """
        Метод, возвращающий полную стоимость всех товаров в корзине.
        :return: Полная стоимость.
        """
        return sum(
            data_many.get("count", 0) * Decimal(data_many.get("price", 0))
            for data_many in self.cart.values()
        )

    def get_count_product_in_basket(self, product_pk) -> int:
        """
        Метод, возвращающий количество конкретного товара в корзине.
        :param product_pk: идентификатор товара.
        :return: Количество товара.
        """
        product_id = str(product_pk)
        return self.cart.get(product_id, {}).get("count", 0)

    def get_price_product_in_basket(self, product_pk) -> Decimal:
        """
        Метод, возвращающий цену конкретного товара в корзине.
        :param product_pk: идентификатор товара.
        :return: Цена товара.
        """
        product_id = str(product_pk)
        return Decimal(self.cart.get(product_id, {}).get("price", 0))
