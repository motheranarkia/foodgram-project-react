from rest_framework import serializers

from recipes.models import Favorite, Recipe


class FavoriteValidateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe',
        )
        read_only_fields = (
            'user',
            'recipe',
        )

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        recipe = self.context.get('recipe')
        recipe_in_favorite = Favorite.objects.filter(
            user=user, recipe=recipe)
        if request.method == 'POST':
            if recipe_in_favorite.exists():
                raise serializers.ValidationError({
                    'errors': 'Этот рецепт уже есть в избранном!'
                })
        if request.method == 'DELETE' and not recipe_in_favorite.exists():
            raise serializers.ValidationError({
                'errors': 'Этого рецепта нет в избранном пользователя!'
            })
        return data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
