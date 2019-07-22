from rest_framework import serializers
import json
from django.utils import timezone

from accounts.serializers import CurrentTeamDefault
from analyst.models import Question, DataSource
from analyst.tasks import get_next_cron_date_time


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


class QuestionModelSerializer(serializers.ModelSerializer):
    team = serializers.HiddenField(
        default=CurrentTeamDefault()
    )
    chart_config = JSONField(required=False)

    class Meta:
        model = Question
        fields = '__all__'

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        if 'cron' not in data:
            data['cron'] = '0 9 * * *'
        cron_config = data['cron']
        now = timezone.now()
        next_run_time = get_next_cron_date_time(cron_config, now)
        consecutive_run_time = get_next_cron_date_time(cron_config, next_run_time)
        if (consecutive_run_time - next_run_time).total_seconds() < 30 * 60:
            raise serializers.ValidationError('please schedule at least with a 30 minutes difference')
        data['next_scheduled_run_time'] = next_run_time
        return data


class DatSourceModelSerializer(serializers.ModelSerializer):
    team = serializers.HiddenField(
        default=CurrentTeamDefault()
    )
    connection = JSONField()
    ssh_tunnel = JSONField(required=False)

    class Meta:
        model = DataSource
        fields = '__all__'
