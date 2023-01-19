from rest_framework import serializers
from newsfinder.models import News, Channel


class NewsSerializer(serializers.ModelSerializer):
    word_count = serializers.IntegerField(required=False)
    date = serializers.DateTimeField(format="%d-%b-%Y", required=False, read_only=True, allow_null=True)

    class Meta(object):
        model = News
        fields = '__all__'


class ListNewsSerializer(serializers.ModelSerializer):
    channel_name = serializers.CharField(source='channel.name', allow_null=True)

    class Meta(object):
        model = News
        fields = ('title', 'url', 'source', 'published_date', 'channel_name')


class ChannelSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = Channel
        fields = '__all__'
