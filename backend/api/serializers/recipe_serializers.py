from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from recipes.models import IngredientList, Recipe, Tag

from .ingredient_serializers import (
    IngredientRecipeCreateSerializer,
    IngredientRecipeListSerializer
)
from .tag_serializer import TagSerializer
from .user_serializers import UserSerializer

REQUIRED_FIELDS_RECIPE = (
    'ingredients', 'tags',
    'name', 'text', 'cooking_time', 'author', 'image'
)
ERROR_MISSING_INGREDIENT = 'Пожалуйста, выберите хотя бы один ингредиент'
ERROR_NOT_POSITIVE_VALUE = 'Пожалуйста, введите хоть что-нибудь'


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeListSerializer(
        many=True,
        # source='ingredient_recipe',
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = REQUIRED_FIELDS_RECIPE + (
            'id', 'is_favorited', 'is_in_shopping_cart'
        )

    def get_user(self):
        return self.context.get('request').user

    def get_request(self):
        return self.context.get('request')

    def get_is_favorited(self, obj):
        request = self.get_request()
        user = self.get_user()
        if not request or request.user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.get_request()
        user = self.get_user()
        if not request or request.user.is_anonymous:
            return False
        return user.shopping_carts.filter(recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = REQUIRED_FIELDS_RECIPE + ('id',)

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError({'ingredients': ERROR_MISSING_INGREDIENT})
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Такой уже выбран'
                })
            ingredients_list.append(ingredient_id)
        return data

    def _add_ingredients(self, ingredients, recipe):
        IngredientList.objects.bulk_create(
            [
                IngredientList(
                    ingredient_id=ingredient.get('id'),
                    recipe=recipe,
                    amount=ingredient['amount']
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=author,
            **validated_data
        )
        self._add_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.pop('name', instance.name)
        instance.image = validated_data.pop('image', instance.image)
        instance.text = validated_data.pop('text', instance.text)
        instance.cooking_time = validated_data.pop(
            'cooking_time',
            instance.cooking_time
        )
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(ingredients, instance)
        instance.tags.clear()
        tags = validated_data.pop('tags')
        self.create_tags(tags, instance)
        return super().update(instance, validated_data)

    def to_representation(self, recipe):
        data = RecipeListSerializer(
            recipe,
            context={'request': self.context.get('request')}).data
        return data
