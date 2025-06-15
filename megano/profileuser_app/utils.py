import re
from json import JSONDecodeError, loads
from string import ascii_lowercase, ascii_uppercase, digits

from django.contrib.auth.models import User
from django.http.request import QueryDict
from rest_framework.exceptions import ValidationError

from .models import ProfileUser


def validate_all_new_user_data(data: dict):
    """
    Проверяет на валидность все пользовательские данные для регистрации
    :param data: Словарь с данными пользователя
    :return: Возвращает ошибку, если данные невалидны
    """
    if User.objects.filter(username=data.get("username", "")).exists():
        raise ValidationError("Пользователь с таким username уже существует.")

    validate_fullname_user(fullname=data.get("name", ""))
    validate_password_user(password=data.get("password", ""))


def get_update_user_data(data: dict, user: ProfileUser) -> tuple:
    """
    Обрабатывает пользовательские данные.
    :param data: Словарь с новыми данными пользователя
    :param user: Экземпляр модели ProfileUser
    :return: Кортеж с обновленной информацией о пользователе
    """
    return (
        data.get("fullName", user.fullName),
        data.get("phone", user.phone),
        data.get("email", user.email),
    )


def validate_fullname_user(fullname: str):
    """
    Функция - валидатор, проверяет корректность полного имени пользователя.
    :param fullname: Имя Фамилия и Отчество
    :return: возвращет ошибку, если пользователь не корректно указал полное имя
    """
    if len(fullname.split()) != 3:
        raise ValidationError(PERSONAL_DATA_ERROR)

    if any(letter.isdigit() for letter in fullname):
        raise ValidationError("В полном имени не должно быть цифр.")


def validate_phone_user(old_phone: str, new_phone: str):
    """
    Проверяет введенный номер на корректность.
    :param old_phone: Старый номер телефона
    :param new_phone: Новый номер телефона
    :return: Возвращает ошибку, если пользователь с новым номером существует или номер невалиден.
    """
    if re.fullmatch(r"Неизвестно|^[78]\d{10}$|^\+7\d{10}$", new_phone) is None:
        raise ValidationError("Некорректный номер телефона")

    if (
        new_phone != "Неизвестно"
        and old_phone != new_phone
        and ProfileUser.objects.filter(phone=new_phone).exists()
    ):
        raise ValidationError("Пользователь с таким номером телефона уже существует.")


def check_email_user_exists(old_email: str, new_email: str):
    """
    Проверяет введенный email на уникальность.
    :param old_email: Старый email
    :param new_email: Новый email
    :return: Возвращает ошибку, если пользователь с новым email существует.
    """
    if old_email != new_email and ProfileUser.objects.filter(email=new_email).exists():
        raise ValidationError("Пользователь с таким email уже существует.")


def check_username_exists(username: str):
    """
    Проверяет введенный username на уникальность.
    :param username: username пользователя (логин)
    :return: Возвращает ошибку, если пользователь с таким username существует
    """
    if User.objects.filter(username=username).exists():
        raise ValidationError("Пользователь с таким username уже существует.")


def validate_password_user(password: str):
    """
    Функция - валидатор. Проверяет надежность пароля.
    :param password: пароль пользователя
    :return: возвращет ошибку, если пароль ненадежен.
    """

    if not all(
        [
            any((sym in ascii_lowercase) for sym in password),
            any((sym in ascii_uppercase) for sym in password),
            any((sym in digits) for sym in password),
            len(password) > 7,
        ]
    ):
        raise ValidationError(WEAK_PASSWORD_ERROR)


def validate_file(namefile: str, size: int):
    """
    Проверяет файл с аватаром пользователя
    :param namefile: Имя файла
    :param size: Размер файла
    :return: Возвращает ошибку, если расширение или размер файла невалидны.
    """

    if not namefile.endswith((".jpg", ".png", ".jpeg", ".gif")):
        raise ValidationError("Файл должен быть изображением")

    if not size < 2_097_152:
        raise ValidationError("Размер файла не должен превышать 2МБ")


def get_classic_dict(dict_string: QueryDict[str] | dict) -> dict:
    """
    Преобразовывает строковой первый ключ QueryDict в обычный словарь.
    Или возвращает переданный словарь, если поймает исключение.
    :param dict_string: QueryDict или dict
    :return: словарь из переданных пользователем данных
    """
    for nice_dict in dict_string:
        try:
            username_and_psw_dict = loads(nice_dict)
            return username_and_psw_dict
        except JSONDecodeError:
            return dict_string


def get_data_new_user(data_user: dict) -> tuple:
    """
    Обрабатывает полное имя пользователя.
    :param data_user: Словарь с данными пользователя
    :return: Кортеж из имени, фамилии и отчества пользователя.
    """
    name, surname, patronymic = data_user.get("first_name", "Н. Н. Н.").split()
    return (
        name,
        surname,
        patronymic,
        data_user.get("username", ""),
        data_user.get("password", ""),
    )


def create_new_user(name: str, surname: str, login_user: str, psw_user: str) -> User:
    """
    Создает нового пользователя.
    :param name: Имя пользователя
    :param surname: Фамилия пользователя
    :param login_user: Логин пользователя
    :param psw_user: Пароль пользователя
    :return: Созданный пользователь
    """
    new_user: User = User.objects.create_user(username=login_user, password=psw_user)
    new_user.first_name, new_user.last_name = name, surname
    new_user.save()
    return new_user


def create_profile_new_user(new_user: User, name: str, surname: str, patronymic: str):
    """
    Создает расширенный профиль нового пользователя.
    :param new_user: Экземпляр модели  User
    :param name: Имя пользователя
    :param surname: Фамилия пользователя
    :param patronymic: Отчество пользователя
    """
    profile_new_user: ProfileUser = ProfileUser.objects.create(user=new_user)
    profile_new_user.fullName = f"{name} {surname} {patronymic}"
    profile_new_user.save()


WEAK_PASSWORD_ERROR = (
    "Пароль должен состоять минимум из 8 символов.\n"
    "В нем должны быть буквы в верхнем и нижнем регистрах латинского алфавита, цифры и спецсимволы"
)

PERSONAL_DATA_ERROR = "Нужно ввести имя, фамилию и отчество через пробел"
