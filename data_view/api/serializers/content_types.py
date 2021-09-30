from rest_framework import serializers
from ...models import (
    ContentTypes,
)

class ContentTypesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentTypes
        fields = [
            "id", 
            "type_name",
            "description"
            ]