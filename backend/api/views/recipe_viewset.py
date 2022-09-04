# import csv

from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from api.filters import RecipeFilter
# from api.permissions import AdminOrAuthor
# from api.serializers.favorite_serializer import (
#     FavoriteListSerializer,
#     FavoriteSerializer
# )
from api.serializers.recipe_serializers import (
    RecipeCreateSerializer,
    RecipeListSerializer,
    RepresentationSerializer
)
# from api.serializers.shoppingcart_serializers import (
#     ShoppingCartSerializer, ShoppingCartValidateSerializer)
from api.permissions import IsAuthorOrAdminOrReadOnly
from recipes.models import Favorite, IngredientList, Recipe, ShoppingCart


RECIPE_DELETED_FROM_SHOP_CART = 'Рецепт успешно удален из списка покупок'
RECIPE_DELETED_FROM_FAVOR = 'Рецепт успешно удален из избранного'


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeListSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        pagination_class=None,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientList.objects.filter(
            recipe__shopping_carts__user=user
        ).order_by(
            'ingredient__name'
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(sum_amount=Sum('amount'))
        shopping_cart = recipe_formation(ingredients)
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(
        detail=False,
        methods=('post', 'delete'),
        url_path=r'(?P<id>[\d]+)/shopping_cart',
        url_name='shopping_cart',
        pagination_class=None,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, id):
        return post_delete_favorite_shopping_cart(
            request.user, request.method, ShoppingCart, id
        )

    @action(
        detail=False,
        methods=('post', 'delete'),
        url_path=r'(?P<id>[\d]+)/favorite',
        url_name='favorite',
        pagination_class=None,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, id):
        return post_delete_favorite_shopping_cart(
            request.user, request.method, Favorite, id
        )


def post_delete_favorite_shopping_cart(user, method, model, id):
    recipe = get_object_or_404(Recipe, id=id)
    if method == 'POST':
        model.objects.create(user=user, recipe=recipe)
        serializer = RepresentationSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    obj = get_object_or_404(model, user=user, recipe=recipe)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def recipe_formation(ingredients):
    return '\n'.join([
        f'{ingredient["ingredient__name"]} - {ingredient["sum_amount"]}'
        f'{ingredient["ingredient__measurement_unit"]}'
        for ingredient in ingredients
    ])
