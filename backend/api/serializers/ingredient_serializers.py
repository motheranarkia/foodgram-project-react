from rest_framework import serializers

from recipes.models import Ingredient, IngredientList

REQUIRED_FIELDS_INGRD = (
    'id',
    'name',
    'measurement_unit',
)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""
    class Meta:
        model = Ingredient
        fields = REQUIRED_FIELDS_INGRD


class IngredientRecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента для RecipeListSerializer."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientList
        fields = REQUIRED_FIELDS_INGRD + ('amount',)


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField(source='ingredient.id')
    # amount = serializers.IntegerField()
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientList
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0!'
            )
        return value
