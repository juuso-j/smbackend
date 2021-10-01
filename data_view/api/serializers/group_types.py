from rest_framework import serializers
from ...models import (
    GroupTypes,
)

class GroupTypesSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupTypes
        fields = [
            "id", 
            "type_name",
            "description"
            ]