from rest_framework import serializers

from recipes.models import Favorite, Recipe

REQUIRED_FIELDS_FAVOR = (
    'user',
    'recipe',
)
ERR_RECIPE_ALREADY_IN_FAVOR = 'Этот рецепт уже есть в избранном!'
ERROR_RECIPE_NOT_IN_FAVOR = 'Этого рецепта нет в избранном пользователя!'


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = "__all__"


class FavoriteListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = REQUIRED_FIELDS_FAVOR
        read_only_fields = REQUIRED_FIELDS_FAVOR

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        recipe = self.context.get('recipe')
        recipe_in_favorite = Favorite.objects.filter(
            user=user, recipe=recipe)
        if request.method == 'POST':
            if recipe_in_favorite.exists():
                raise serializers.ValidationError({
                    'errors': ERR_RECIPE_ALREADY_IN_FAVOR
                })
        if request.method == 'DELETE' and not recipe_in_favorite.exists():
            raise serializers.ValidationError({
                'errors': ERROR_RECIPE_NOT_IN_FAVOR
            })
        return data
