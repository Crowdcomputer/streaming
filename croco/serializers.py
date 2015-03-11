from rest_framework import serializers

from croco.models import Event, Task


__author__ = 'Stefano Tranquillini <stefano.tranquillini@gmail.com>'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('type', 'factor', 'message_name')


class TaskSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

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
        fields = ("id", "name", "events", "data_name", "activiti_definition_id", "completeness", "cf_id")
        read_only = ("executions")

