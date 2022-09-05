import csv

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
from api.serializers.favorite_serializers import FavoriteSerializer
from api.serializers.recipe_serializers import (
    RecipeCreateSerializer,
    RecipeListSerializer,
    RepresentationSerializer
)
from api.serializers.shoppingcart_serializers import ShoppingCartSerializer
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

    def get_list(self, request, list_model, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_list = list_model.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if not in_list:
                list_objects = list_model.objects.create(user=user,
                                                         recipe=recipe)
                if isinstance(list_model, Favorite):
                    serializer = FavoriteSerializer(list_objects.recipe)
                else:
                    serializer = ShoppingCartSerializer(list_objects.recipe)
                return Response(data=serializer.data,
                                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not in_list:
                data = {'errors': 'Этого рецепта нет в списке.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            in_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('GET',),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        pagination_class=None,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredient_list = IngredientList.objects.filter(
            recipe__shopping_cart__user=request.user
        )
        return list_information(ingredient_list)

    @action(
        methods=['DELETE', 'POST'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        return self.get_list(request=request, list_model=ShoppingCart, pk=pk)

    # @action(
    #     detail=False,
    #     methods=('POST', 'DELETE'),
    #     url_path=r'(?P<id>[\d]+)/shopping_cart',
    #     url_name='shopping_cart',
    #     pagination_class=None,
    #     permission_classes=[IsAuthenticated]
    # )
    # def shopping_cart(self, request, id):
    #     return post_delete_favorite_shopping_cart(
    #         request.user, request.method, ShoppingCart, id
    #     )

    # @action(
    #     detail=False,
    #     methods=('post', 'delete'),
    #     url_path=r'(?P<id>[\d]+)/favorite',
    #     url_name='favorite',
    #     pagination_class=None,
    #     permission_classes=[IsAuthenticated]
    # )
    # def favorite(self, request, id):
    #     return post_delete_favorite_shopping_cart(
    #         request.user, request.method, Favorite, id
    #     )

    @action(
        methods=['DELETE', 'POST'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        return self.get_list(request=request, list_model=Favorite, pk=pk)


def post_delete_favorite_shopping_cart(user, method, model, id):
    recipe = get_object_or_404(Recipe, id=id)
    if method == 'POST':
        model.objects.create(user=user, recipe=recipe)
        serializer = RepresentationSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    obj = get_object_or_404(model, user=user, recipe=recipe)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def list_information(ingredient_list):
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
