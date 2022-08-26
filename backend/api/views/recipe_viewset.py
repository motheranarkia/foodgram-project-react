import csv

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http.response import HttpResponse
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action

from api.serializers.recipe_serializers import RecipeListSerializer, \
    RecipeCreateSerializer
from api.serializers.shoppingcart_serializers import ShoppingCartSerializer, \
    ShoppingCartValidateSerializer
from api.serializers.favorite_serializer import FavoriteSerializer, \
    FavoriteListSerializer
from api.filters import RecipeFilter
from api.permissions import AuthorOrReadOnly
from recipes.models import Recipe, IngredientList, ShoppingCart, Favorite


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = (AuthorOrReadOnly,)
    filterset_class = RecipeFilter
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
        return unloading_shopping_cart(ingredient_list)

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
        recipe_in_cart = ShoppingCart.objects.filter(
            user=current_user,
            recipe=recipe
        )
        recipe_in_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        recipe_in_favorite = Favorite.objects.filter(
            user=current_user, recipe=recipe
        )
        recipe_in_favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def unloading_shopping_cart(ingredient_recipe):
    ingredients = ingredient_recipe.values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(ingredient_amount=Sum('amount')).values_list(
        'ingredient__name', 'ingredient_amount',
        'ingredient__measurement_unit',
    )
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = ('attachment;'
                                       'filename="Shoppingcart.csv"')
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    for item in list(ingredients):
        writer.writerow(item)
    return response
