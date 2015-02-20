from rest_framework import serializers

from croco.models import Event, Task, TaskData
from croco.utils import process_events


__author__ = 'Stefano Tranquillini <stefano.tranquillini@gmail.com>'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('type', 'factor','message_name')


class TaskSerializer(serializers.ModelSerializer):
    pk = serializers.ReadOnlyField()

    # data = serializers.SlugRelatedField(many=True, read_only=True, slug_field="get_data")
    events = EventSerializer(many=True, read_only=False)
    completeness = serializers.FloatField(read_only=True)

    def create(self, validated_data):
        events = validated_data.pop('events')
        task = Task.objects.create(**validated_data)
        for event in events:
            event['task'] = task
            Event.objects.create(**event)
        return task

    class Meta:
        model = Task
        fields = ("pk", "name", "events", "data_name", "activiti_definition_id", "completeness")
        read_only = ("cf_id", "executions")

