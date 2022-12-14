from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag, Ingredient


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр для сортировки рецептов."""
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(
                favorites__user=self.request.user
            )
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(shopping_carts__user=self.request.user)

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author', 'is_favorited', 'is_in_shopping_cart'
        )
