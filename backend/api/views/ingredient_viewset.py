# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.serializers.ingredient_serializers import IngredientSerializer
from recipes.models import Ingredient
from api.filters import IngredientFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_class = IngredientFilter
