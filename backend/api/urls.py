from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.ingredient_viewset import IngredientViewSet
from api.views.recipe_viewset import RecipeViewSet
from api.views.tag_viewset import TagViewSet
from api.views.user_viewset import UserViewSet

app_name = 'api'

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
