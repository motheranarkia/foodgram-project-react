from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from api.serializers.ingredient_serializers import IngredientSerializer
from recipes.models import Ingredient
from api.permissions import AdminOrReadOnly


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    search_fields = ('^name',)

# 4
