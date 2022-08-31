from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.follow_serializers import FollowListSerializer
from api.serializers.user_serializers import UserSerializer
from users.models import Follow, User

ERROR_SUBSCRIPTION_ALREADY_EXISTS = 'Вы уже подписаны на этого автора.'
ERROR_SUBSCRIBING_NOT_EXIST = 'Вы не подписаны на этого автора.'


class UserViewSet(UserViewSet):
    """Вьюсет для модели пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(follower__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowListSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['get', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        subscribe = Follow.objects.filter(user=user, author=author)
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'GET':
            if subscribe.exists():
                data = {
                    'errors': ERROR_SUBSCRIPTION_ALREADY_EXISTS}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, author=author)
            serializer = FollowListSerializer(
                author,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if not subscribe.exists():
                data = {'errors': ERROR_SUBSCRIBING_NOT_EXIST}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
