from rest_framework import serializers

from core.models import Tag


class TagSelializer(serializers.ModelSerializer):
    '''tagモデルのserializer
    '''

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id', )
