from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from users.models import Follow, User
from api.serializers.follow_serializers import (
    FollowSerializer, FollowListSerializer
)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = get_object_or_404(
            User,
            id=request.user.id
        )
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        if pages is not None:
            serializer = FollowListSerializer(
                pages,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowListSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        methods=('post', 'delete'),
        detail=True,
        url_path='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def subscription_actions(self, request, id):
        user = request.user
        if request.method == 'POST':
            data = {'user': user.id, 'author': id}
            serializer = FollowSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        following = get_object_or_404(User, id=id)
        follow = get_object_or_404(
            Follow, user=user, author=following
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
