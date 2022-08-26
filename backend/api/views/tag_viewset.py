from rest_framework import viewsets

from recipes.models import Tag
from api.serializers.tag_serializer import TagSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
