from rest_framework import serializers

from recipes.models import Recipe, ShoppingCart


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', )


class ShoppingCartValidateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
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
        recipe_in_cart = ShoppingCart.objects.filter(
            user=user, recipe=recipe)
        if request.method == 'POST':
            if recipe_in_cart.exists():
                raise serializers.ValidationError({
                    'errors': 'Этот рецепт уже добавлен в корзину покупок!'
                })
        if request.method == 'DELETE' and not recipe_in_cart.exists():
            raise serializers.ValidationError({
                'errors': 'Этого рецепта нет в корзине покупок пользователя!'
            })
        return data
