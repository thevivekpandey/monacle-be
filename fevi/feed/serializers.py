from rest_framework import serializers
import json

from feed.models import (
    FeedCard,
    Comment,
    Adept
)
from accounts.models import User
from analyst.serializers import CurrentTeamDefault

from rest_framework.compat import unicode_to_repr


class CurrentFeedCardDefault(object):
    def set_context(self, serializer_field):
        self.feed_card = serializer_field.context['request'].feed_card

    def __call__(self):
        return self.feed_card

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)


class JSONField(serializers.Field):
    default_error_messages = {
        'invalid': 'Value must be valid JSON.'
    }

    def __init__(self, *args, **kwargs):
        self.binary = kwargs.pop('binary', False)
        super(JSONField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        try:
            return json.dumps(data)
        except (TypeError, ValueError):
            self.fail('invalid')

    def to_representation(self, value):
        return json.loads(value)


class CommentModelSerializer(serializers.ModelSerializer):
    team = serializers.HiddenField(
        default=CurrentTeamDefault()
    )
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    feed_card = serializers.HiddenField(
        default=CurrentFeedCardDefault()
    )

    class Meta:
        model = Comment
        fields = '__all__'


class AdeptModelSerializer(serializers.ModelSerializer):
    team = serializers.HiddenField(
        default=CurrentTeamDefault()
    )
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    feed_card = serializers.HiddenField(
        default=CurrentFeedCardDefault()
    )

    class Meta:
        model = Adept
        fields = '__all__'


class UserModelCommentSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('name', 'id')

    def get_name(self, obj):
        return obj.first_name + ' ' + obj.last_name


class CommentReadModelSerializer(serializers.ModelSerializer):
    user = UserModelCommentSerializer()

    class Meta:
        model = Comment
        fields = ('user', 'text', 'id', 'created')


class AdeptReadModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adept
        fields = ('user', 'id')


class AdeptSingleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adept
        fields = '__all__'


class FeedCardModelSerializer(serializers.ModelSerializer):
    comments = CommentReadModelSerializer(many=True, read_only=True)
    adepts = serializers.SerializerMethodField('get_adepts_count')
    is_adept = serializers.SerializerMethodField('is_user_adept')
    data = JSONField()

    class Meta:
        model = FeedCard
        fields = '__all__'

    def is_user_adept(self, obj):
        if 'request' not in self.context:
            return False
        user = self.context['request'].user
        return obj.adepts.filter(team=obj.team, user=user).exists()

    def get_adepts_count(self, obj):
        return obj.adepts.filter(team=obj.team).count()
