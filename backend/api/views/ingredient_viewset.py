from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.serializers.ingredient_serializers import IngredientSerializer
from recipes.models import Ingredient
from api.filters import IngredientFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели ингредиентов."""
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    # pagination_class = None
    filterset_class = IngredientFilter
