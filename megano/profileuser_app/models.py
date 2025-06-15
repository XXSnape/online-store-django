from django.db import models
from django.contrib.auth.models import User


def avatar_path(instance: "AvatarUser", filename: str) -> str:
    """
    Функция генерирует путь до файла с аватаром пользователя.

    :param instance: Класс AvatarUser
    :param filename: Имя файла
    :return: Путь до файла
    """
    return "users/avatars/id_{pk}/{filename}".format(
        pk=instance.profile.pk, filename=filename
    )


class ProfileUser(models.Model):
    """
    Модель-класс. Содержит расширенную информацию о пользователе.
    """

    fullName = models.CharField(
        max_length=64, default="Неизвестно", blank=False, verbose_name="Ф.И.О."
    )
    email = models.EmailField(
        max_length=64, default="Неизвестно", blank=False, verbose_name="Email-адрес"
    )
    phone = models.CharField(
        max_length=32, default="Неизвестно", blank=False, verbose_name="Номер телефона"
    )
    user: User = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
        ordering = ("pk",)

    def __str__(self):
        return "#{id} {name}".format(id=self.user.pk, name=self.user.username)


class AvatarUser(models.Model):
    """
    Модель-класс. Содержит в себе аватар пользователя.
    """

    avatar = models.ImageField(upload_to=avatar_path, default="", verbose_name="Аватар")
    profile = models.OneToOneField(
        ProfileUser,
        on_delete=models.CASCADE,
        related_name="avatar",
        verbose_name="Профиль пользователя",
    )

    class Meta:
        verbose_name = "Аватар пользователя"
        verbose_name_plural = "Аватары пользователей"
        ordering = ("pk",)

    def __str__(self):
        return "#{id} {name} avatar".format(
            id=self.profile.pk, name=self.profile.user.username
        )

    def src(self):
        return "/media/{avatar_path}".format(avatar_path=self.avatar)

    def alt(self):
        return "#{id} {name} avatar".format(
            id=self.profile.pk, name=self.profile.user.username
        )
