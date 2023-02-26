from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel

User = get_user_model()


class Post(CreatedModel):
    """
    Модель для управления записями проекта. В модели описаны поля:
    текст, дата, поле с ссылкой на другую модель 'Users'
    """
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу для вашего поста'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Добавьте картинку к своему посту'
    )

    class Meta:
        """
        Укажем по умолчанию фильтрацию по дате по убыванию.
        """
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text


class Group(models.Model):
    """
    Модель для разделения постов по сообществам. В модели описаны поля:
    название группы, адрес, описание сообщества.
    """
    title = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Адрес'
    )
    description = models.TextField(
        verbose_name='Описание'
    )

    def __str__(self):
        return self.title


class Comment(CreatedModel):
    """
    Модель для добавления комментариев к постам. В модели описаны поля:
    текст, дата, автор поле с ссылкой на другую модель 'Users',
    ссылка на моделль поста.
    """
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Добавьте комментарий к посту'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )

    class Meta:
        """
        Укажем по умолчанию фильтрацию по дате по убыванию.
        """
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Follow(models.Model):
    """
    Модель-система подписки на авторов.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )

    class Meta:
        """Уникальное значение для сочетания автор-подписчик."""
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'], name='unique_follow'
            )
        ]
