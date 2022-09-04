# from rest_framework import serializers

# from recipes.models import Recipe, ShoppingCart

# ERROR_RECIPE_ALREADY_IN_LIST = 'Этот рецепт уже добавлен в список покупок'
# ERROR_RECIPE_NOT_IN_LIST = 'Этого рецепта нет в списке покупок'

# REQUIRED_FIELDS_SHOP_CART = (
#     'user',
#     'recipe',
# )


# class ShoppingCartSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Recipe
#         fields = "__all__"


# class ShoppingCartValidateSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = ShoppingCart
#         fields = REQUIRED_FIELDS_SHOP_CART
#         read_only_fields = REQUIRED_FIELDS_SHOP_CART

#     def validate(self, data):
#         request = self.context.get('request')
#         user = request.user
#         recipe = self.context.get('recipe')
#         recipe_in_cart = ShoppingCart.objects.filter(
#             user=user, recipe=recipe)
#         if request.method == 'POST':
#             if recipe_in_cart.exists():
#                 raise serializers.ValidationError({
#                     'errors': ERROR_RECIPE_ALREADY_IN_LIST
#                 })
#         if request.method == 'DELETE' and not recipe_in_cart.exists():
#             raise serializers.ValidationError({
#                 'errors': ERROR_RECIPE_NOT_IN_LIST
#             })
#         return data
