from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import AvatarUser, ProfileUser
from .utils import validate_password_user


class AuthUserSerializer(serializers.Serializer):
    """
    Класс-сериализатор. Имеет поля username и пароль.
    """

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """
        Метод-валидатор. Проверяет данные и аутентифицирует пользователя в системе или вызывает исключение.

        :param data: проверяемые данные
        :return: проверенные данные или исключения.
        """
        user = authenticate(
            username=data.get("username", ""), password=data.get("password", "")
        )
        if not user:
            raise ValidationError("Неправильный логин или пароль.")
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Класс-сериализатор. Основан на модели стандартного пользователя.
    """

    name = serializers.CharField(source="first_name")

    class Meta:
        model = User
        fields = (
            "name",
            "username",
            "password",
        )


class AvatarUserSerializer(serializers.ModelSerializer):
    """
    Класс-сериализатор. Основан на модели аватара пользователя.
    """

    class Meta:
        model = AvatarUser
        fields = (
            "src",
            "alt",
        )


class ProfileUserSerializer(serializers.ModelSerializer):
    """
    Класс-сериализатор. Основан на модели расширенного пользовательского профиля и его аватара.
    """

    avatar = AvatarUserSerializer(many=False, required=False)

    class Meta:
        model = ProfileUser
        fields = (
            "fullName",
            "email",
            "phone",
            "avatar",
        )


class ChangePasswordUserSerializer(serializers.Serializer):
    """
    Класс-сериализатор. Имеет поля текущий пароль и новый.
    """

    currentPassword = serializers.CharField()
    newPassword = serializers.CharField()

    def validate(self, data):
        """
        Метод-валидатор. Проверяет данные и аутентифицирует пользоваетеля в системе или вызвает исключения.

        :param data: проверяемые данные
        :return: проверенные данные или исключения.
        """
        validate_password_user(password=data.get("newPassword"))

        if data.get("newPassword") == data.get("currentPassword", ""):
            raise ValidationError("Пароли совпадают.")

        user = authenticate(
            username=self.context.get("request").user.username,
            password=data.get("currentPassword", ""),
        )
        if not user:
            raise ValidationError("Неверный пароль.")
        return data

    def save(self, **kwargs):
        """
        Сохраняет новый пароль и обнавляет хэш в БД.
        :param kwargs: переданные данные.
        :return: сохраняет новый пароль.
        """
        user = self.context.get("request").user
        user.set_password(self.validated_data.get("newPassword"))
        user.save()
        update_session_auth_hash(self.context.get("request"), user)
