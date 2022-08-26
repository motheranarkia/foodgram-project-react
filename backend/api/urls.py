from django.urls import include, path
from rest_framework.routers import DefaultRouter

from views.ingredient_viewset import IngredientViewSet
from views.recipe_viewset import RecipeViewSet
from views.tag_viewset import TagViewSet
from views.user_viewset import UserViewSet

app_name = 'api'

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
