from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from django.db.models.query import QuerySet
from basket_app.basket import Basket
from products_app.models import Product
from profileuser_app.utils import validate_fullname_user
from .models import Order, QuantityProductsInBasket
from decimal import Decimal
from datetime import datetime


def get_nice_data(date: datetime) -> str:
    """
    Обрабатывает дату.
    :param date: объект datetime
    :return: Обработанная строка, в нужном формате
    """
    return datetime.strftime(date, "%d %B %Y, %H:%M:%S")


def get_order_user_or_400(
    request: Request, pk: Order.pk, payment: bool = False
) -> Order:
    """
    Проверяет, что заказ принадлежит пользователю, который делает запрос.
    Если заказ создавал другой пользователь, то возвращается ошибка.
    Если параметр payment установлен в True и заказ оплачен, то возвращается ошибка.

    :param request: Запрос
    :param pk: Идентификатор заказа
    :param payment: Тип Bool. Передается, если пользователь переходит на стадию оплаты заказа
    :return: Возвращается заказ, если валидация данных прошла успешно
    """
    if not payment:
        order = (
            Order.objects.select_related("user_profile")
            .prefetch_related("products")
            .filter(id=pk, user_profile_id=request.user.pk)
            .first()
        )
    else:
        order = (
            Order.objects.select_related("user_profile")
            .prefetch_related("products")
            .filter(id=pk, user_profile_id=request.user.pk, status="unconfirmed")
            .first()
        )
        if order and not all(
            [
                order.fullName,
                order.email,
                order.phone,
                order.deliveryType,
                order.paymentType,
                order.city,
                order.address,
            ]
        ):
            raise ValidationError("Заказ содержит не все данные.")

    if not order:
        raise ValidationError(
            "Заказ не принадлежит этому пользователю, или не существует, или уже оплачен."
        )
    return order


def get_detail_order_data(order_data: dict) -> tuple:
    """
    Обрабатывает детальную информацию о заказе и возвращает ошибку, если данные отсутствуют.
    :param order_data: Данные о заказе
    :return: Детальная информация о заказе.
    """
    data_order = tuple(
        order_data.get(info)
        for info in [
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "city",
            "address",
        ]
    )
    if all(data_order):
        return data_order
    raise ValidationError("Не все данные заполены корректно.")


def get_detail_payment_data(payment_data: dict) -> tuple:
    """
    Обрабатывает информацию о карте пользователя.
    :param payment_data: Словарь с информацией о карте пользователя
    :return: Кортеж с информацией о карте пользователя
    """
    return tuple(
        payment_data.get(info) for info in ["number", "name", "month", "year", "code"]
    )


def save_number_products_in_basket(order_pk: Order.pk, products: QuerySet, bk: Basket):
    """
    Сохраняет количество товара в корзине на момент оформления заказа в базу данных.
    :param order_pk: Идентификатор заказа
    :param products: QuerySet с товарами
    :param bk: Экземпляр класса Basket
    """
    for product in products:
        QuantityProductsInBasket.objects.create(
            order_id=order_pk,
            product_id=product.pk,
            quantity=bk.get_count_product_in_basket(product_pk=product.pk),
        )


def setup_order(order: Order, params: tuple) -> None:
    """
    Изменяет запись с заказом в базе данных, заполняя ее пользовательскими данными.
    Если пользователь хочет изменить запись с уже оплаченным заказом, возвращается ошибка.
    :param order: Запись заказа в базе данных
    :param params: Пользовательские данные.
    :return: None
    """
    if order.status != "unconfirmed":
        raise ValidationError("Заказ уже оплачен.")
    (
        order.fullName,
        order.email,
        order.phone,
        order.deliveryType,
        order.paymentType,
        order.city,
        order.address,
    ) = params


def setup_count_products_in_basket(order_pk: Order.pk, data: dict):
    """
    Модифицирует сериализованные данные.
    Значение поля count с информацией о количестве товара на складе заменяет на количество товара в корзине.
    :param order_pk: Идентификатор заказа
    :param data: Сериализованные данные
    """
    for index in range(len(data.get("products", list()))):
        product_info: QuantityProductsInBasket = (
            QuantityProductsInBasket.objects.filter(
                order_id=order_pk, product_id=data["products"][index]["id"]
            ).first()
        )

        data["products"][index]["count"] = product_info.quantity


def remove_goods_from_warehouse(order: Order, bk: Basket):
    """
    Уменьшает количество товара на складе после оформления покупки.
    :param order: Экземпляр модели Order
    :param bk: Экземпляр класса Basket
    :return: Уменьшает количество товара на складе
    """
    for item in order.products.all():
        product = Product.objects.get(id=item.pk)
        product.count -= bk.get_count_product_in_basket(product_pk=product.pk)
        product.save()


def check_delivery_type_and_price_setting(order: Order):
    """
    Проверяет тип доставки. При express доставке стоимость заказа увеличивается на 500$.
    При обычной доставке если стоимость заказа не превышает 2000$, то она увеличивается на 200$.
    :param order: Экземпляр модели Order
    :return: Измененная запись с заказом.
    """
    if order.deliveryType == "express":
        order.totalCost += Decimal(500)
    else:
        if order.totalCost < 2000:
            order.totalCost += Decimal(200)


def validation_all_data(name: str, number: str, month: str, year: str, code: str):
    """
    Проверяет данные карты пользователя.
    :param name: Полное имя пользователя
    :param number: Номер карты
    :param month: Месяц
    :param year: Год
    :param code: CVV - код
    :return: Возвращает ошибку, если данные не прошли проверку на валидность.
    """
    if not all(data.isdigit() for data in [number, month, year, code]):
        raise ValidationError("Даты и данные карты должны быть числом")

    if int(month) not in range(1, 13):
        raise ValidationError("Месяц должен быть в пределах от 1 до 12.")

    if int(year) not in range(1970, 2200):
        raise ValidationError("Невалидный год.")

    if int(number) % 2 != 0:
        raise ValidationError("Номер карты должен быть четным.")

    if len(number) > 8:
        raise ValidationError("Номер карты не должен быть длиннее 8 цифр.")

    if number[-1] == "0":
        raise ValidationError("Номер карты не должен заканчиваться на ноль.")

    if len(code) != 3:
        raise ValidationError("CVV-код должен быть трезначным.")

    validate_fullname_user(fullname=name)
