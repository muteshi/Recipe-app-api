from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer class for tag object
    """

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer class for ingredient object
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_Fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer class for recipe object
    """
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'duration', 'link', 'price',
                  'ingredients', 'tags')
        read_only_Fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializer class for recipe object details view
    """
    ingredients = IngredientSerializer(
        many=True,
        read_only=True
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )


class RecipeImageSerializer(serializers.ModelSerializer):
    """
    Serializer class for downloading images to recipe model
    """
    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)
