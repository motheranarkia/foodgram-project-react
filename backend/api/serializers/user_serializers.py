from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import SerializerMethodField

from users.models import Follow, User

REQUIRED_FIELDS_USER = (
    'id',
    'email',
    'username',
    'first_name',
    'last_name',
)


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""

    class Meta:
        model = User
        fields = REQUIRED_FIELDS_USER + ('password',)


class UserSerializer(UserSerializer):
    """Сериализатор пользователей."""
    is_subscribed = SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            author=obj
        ).exists()

    class Meta:
        model = User
        fields = REQUIRED_FIELDS_USER + ('is_subscribed',)

# почти рабочий вариант
