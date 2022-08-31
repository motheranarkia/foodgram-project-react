from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from api.permissions import AdminOrReadOnly
from api.serializers.ingredient_serializers import IngredientSerializer
from recipes.models import Ingredient


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    search_fields = ('^name',)
