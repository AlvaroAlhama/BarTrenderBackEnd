from rest_framework import serializers
from .models import *


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name', 'type', 'photo_url')


class EstablishmentSerializer(serializers.ModelSerializer):

    tags = serializers.SerializerMethodField()

    class Meta:
        model = Establishment
        exclude = ('image',)
        include = ('tags')

    def get_tags(self, establishment):
        request = self.context.get('request')

        tags = establishment.tags
        serializer = TagsSerializer(tags, many=True, read_only=True, context={"request": request})

        return serializer.data


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        exclude = ('clients_id',)

