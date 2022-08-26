from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import SerializerMethodField

from users.models import Follow, User

REQUIRED_FIELDS_USER = (
    "id",
    "email",
    "username",
    "first_name",
    "last_name",
)


# 5
class CreateUserSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = REQUIRED_FIELDS_USER
        extra_kwargs = {'password': {'write_only': True}}


# 5
class UserSerializer(UserSerializer):
    """Сериализатор пользователей."""
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = REQUIRED_FIELDS_USER

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=user,
            author=obj
        ).exists()
