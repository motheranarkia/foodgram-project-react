from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from users.models import Follow, User

REQUIRED_FIELDS_USER = (
    'id', 'username', 'first_name', 'last_name', 'email'
)


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = REQUIRED_FIELDS_USER + ('password',)


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = REQUIRED_FIELDS_USER + ('is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            author=obj
        ).exists()
