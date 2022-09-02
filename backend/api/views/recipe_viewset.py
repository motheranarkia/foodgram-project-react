import csv

from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.permissions import AdminOrAuthor
from api.serializers.favorite_serializer import (
    FavoriteListSerializer,
    FavoriteSerializer
)
from api.serializers.recipe_serializers import (
    RecipeCreateSerializer,
    RecipeListSerializer
)
from api.serializers.shoppingcart_serializers import (
    ShoppingCartSerializer, ShoppingCartValidateSerializer)
from recipes.models import Favorite, IngredientList, Recipe, ShoppingCart

RECIPE_DELETED_FROM_SHOP_CART = 'Рецепт успешно удален из списка покупок'
RECIPE_DELETED_FROM_FAVOR = 'Рецепт успешно удален из избранного'


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = (AdminOrAuthor)
    filter_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredient_list = IngredientList.objects.filter(
            recipe__shopping_cart__user=request.user
        )
        return list_formation(ingredient_list)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        current_user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = ShoppingCartValidateSerializer(
            data=request.data,
            context={'request': request, 'recipe': recipe},
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            ShoppingCart.objects.create(
                user=current_user,
                recipe=recipe
            )
            serializer = ShoppingCartSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        deleted = get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe=recipe
        )
        deleted.delete()
        return Response(
            {'message': RECIPE_DELETED_FROM_SHOP_CART},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        current_user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoriteListSerializer(
            data=request.data,
            context={'request': request, 'recipe': recipe},
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            Favorite.objects.create(user=current_user, recipe=recipe)
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        deleted = get_object_or_404(Favorite,
                                    user=request.user,
                                    recipe=recipe)
        deleted.delete()
        return Response({'message': RECIPE_DELETED_FROM_FAVOR},
                        status=status.HTTP_200_OK)


def list_formation(ingredient_list):
    ingredients = ingredient_list.values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        ingredient_amount=Sum('amount')
    ).values_list(
        'ingredient__name',
        'ingredient_amount',
        'ingredient__measurement_unit',
    )
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment;'
        'filename="Shoppingcart.csv"'
    )
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    for item in list(ingredients):
        writer.writerow(item)
    return response
