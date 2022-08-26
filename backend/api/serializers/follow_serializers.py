from rest_framework import serializers

from recipes.models import Follow, Recipe
from users.models import User


class FollowRecipeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time',
        )


class FollowListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count", read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name',
            'recipes', 'is_subscribed', 'recipes_count',
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj: User):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj: User):
        recipes = obj.recipes.all()
        return FollowRecipeSerializers(recipes, many=True).data
