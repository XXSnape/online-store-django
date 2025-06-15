from products_app.models import Product
from rest_framework.exceptions import ValidationError

from .basket import Basket
from .serializers import BasketSerializer


def get_serialized_data(basket: Basket) -> BasketSerializer.data:
    """
    Сериализует данные. В контекст передает корзину.
    :param basket: Экземпляр класса Basket
    :return: Сериализованные данные.
    """
    return BasketSerializer(
        Product.objects.prefetch_related("review", "product_img", "tags")
        .select_related("category")
        .filter(pk__in=basket.cart.keys()),
        many=True,
        context=basket,
    ).data


def check_user_input_count(
    request_data: dict, product: Product, bk: Basket
) -> int | ValidationError:
    """
    Проверяет количество товара, которое запрашивает пользователь.
    Если товаров на складе меньше запрашиваемого или запрос невалиден, то возвращается ошибка.
    :param request_data: данные из запроса пользователя
    :param product: Экземпляр модели Product
    :param bk: Экземпляр класса Basket
    :return: Количество товаров для пользователя.
    """
    quantity_products_user = int(request_data.get("count", 0))
    if quantity_products_user < 1:
        raise ValidationError(
            "Количество запрашиваемых товаров должно быть больше нуля."
        )

    if (
        bk.cart.get(str(product.pk), {}).get("count", 0) + quantity_products_user
        > product.count
    ):
        raise ValidationError("Количество товаров на складе меньше запрашиваемого.")

    return quantity_products_user
