from django.contrib import admin

from .models import AvatarUser, ProfileUser


class ProfileUserInline(admin.StackedInline):
    """
    Класс для связи расширенного профиля пользователя с его аватаром в административной панели.
    """

    model = AvatarUser


@admin.register(ProfileUser)
class ProfileUserAdmin(admin.ModelAdmin):
    """
    Класс для представления расширенного профиля пользователя в административной панели.
    """

    inlines = [ProfileUserInline]
    list_display = ("pk", "fullName", "email", "phone", "user")
    list_display_links = ("pk", "fullName")
    ordering = ("pk",)


@admin.register(AvatarUser)
class AvatarUserAdmin(admin.ModelAdmin):
    """
    Класс для представления аватара пользователя в административной панели.
    """

    list_display = ("pk", "avatar", "profile")
    ordering = ("pk",)
