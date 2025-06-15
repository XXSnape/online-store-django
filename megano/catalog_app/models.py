from django.db import models


def category_path(instance: "ImageCategory", filename: str) -> str:
    """
    Функция, определяющая путь до файла.
    :param instance: экземпляр класа ImageCategory
    :param filename: имя файла
    :return: путь до файла с изображением категории относительно этой категории, если нет "родителя", иначе от "родителя".
    """
    if instance.category.parent:
        return "categories/images/{sub_cat}/{category}/id_{pk}/{file}".format(
            sub_cat=instance.category.parent,
            category=instance.category,
            pk=instance.category.pk,
            file=filename,
        )
    return "categories/images/{category}/id_{pk}/{file}".format(
        category=instance.category, pk=instance.category.pk, file=filename
    )


class Category(models.Model):
    """
    Модель категории.
    """

    title = models.CharField(
        max_length=64, blank=False, verbose_name="Название категории"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
        verbose_name="Подкатегории",
    )
    main = models.BooleanField(
        default=False, verbose_name="Избранная категория"
    )  # используется для определния, является ли категория избранной

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("pk",)

    def __str__(self):
        return self.title


class ImageCategory(models.Model):
    """
    Модель изображения категории.
    """

    image = models.ImageField(
        upload_to=category_path, default="", verbose_name="Изображение"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="category_img",
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "Изображение категории"
        verbose_name_plural = "Изображения категорий"
        ordering = ("pk",)

    def src(self):
        """
        Метод для сериализатора
        :return: путь до файла
        """
        return "/media/{category_image_path}".format(category_image_path=self.image)

    def alt(self):
        """
        Метод для сериализатора
        :return: возвращает название категории, связанной с изображением.
        """
        return self.category.title

    def __str__(self):
        return "Изображение {category}.".format(category=self.category)
