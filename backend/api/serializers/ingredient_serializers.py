from rest_framework import serializers

from recipes.models import Ingredient, IngredientList

REQUIRED_FIELDS_INGRD = (
    "id",
    "name",
    "measurement_unit",
)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    name = serializers.CharField()
    measurement_unit = serializers.CharField()
    id = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = REQUIRED_FIELDS_INGRD


class IngredientRecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента для RecipeListSerializer."""

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientList
        fields = REQUIRED_FIELDS_INGRD + ('amount')


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(write_only=True)
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'amount'
        ]
