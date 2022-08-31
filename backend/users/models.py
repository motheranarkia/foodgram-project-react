from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_LEN_FIELD = 150
USER_HELP = (
    'Обязательно для заполнения. '
    f'Максимум {MAX_LEN_FIELD} букв.'
)


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        'Уникальный юзернейм',
        max_length=MAX_LEN_FIELD,
        blank=False,
        unique=True,
        help_text=USER_HELP
    )
    password = models.CharField(
        'Пароль',
        max_length=MAX_LEN_FIELD,
        blank=False,
        help_text=USER_HELP
    )
    email = models.CharField(
        max_length=254,
        blank=False,
        verbose_name='Адрес электронной почты',
        help_text='Обязательно для заполнения'
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LEN_FIELD,
        blank=False,
        help_text=USER_HELP
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LEN_FIELD,
        blank=False,
        help_text=USER_HELP
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author', ),
                name='unique_subscribe'),
        )

        def __str__(self):
            return f'{self.user} подписался на {self.author}'
