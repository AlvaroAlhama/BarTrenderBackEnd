from rest_framework import serializers
from .models import *


class TagsSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ('name', 'type', 'photo_url')

    def get_photo_url(self, tag):
        request = self.context.get('request')

        if tag.image:
            return request.build_absolute_uri(tag.image.url)
        else:
            return None


class EstablishmentSerializer(serializers.ModelSerializer):

    tags = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Establishment
        exclude = ('image',)
        include = ('photo_url', 'tags')

    def get_photo_url(self, establishment):
        request = self.context.get('request')

        if establishment.image:
            return request.build_absolute_uri(establishment.image.url)
        else:
            return None

    def get_tags(self, establishment):
        request = self.context.get('request')

        tags = establishment.tags
        serializer = TagsSerializer(tags, many=True, read_only=True, context={"request": request})

        return serializer.data


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        exclude = ('clients_id',)

