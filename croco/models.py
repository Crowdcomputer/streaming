# Create your models here.
import json
from django.db import models


class Event(models.Model):
    EVENT_TYPE = (
        ('M', 'Multiply'),
        ('G', 'Group'),
    )
    type = models.CharField(max_length=1, choices=EVENT_TYPE)
    factor = models.PositiveSmallIntegerField()
    task = models.ForeignKey('Task', related_name='events')


class TaskData(models.Model):
    json_data = models.TextField(default="{}")
    task = models.ForeignKey('Task', related_name='data')

    def set_data(self, data):
        if not isinstance(data, str):
            # expect a dict -> transform to json
            self.json_data = json.dumps(data)
        else:
            self.json_data = data

    @property
    def get_data(self):
        # always return a dict
        return json.loads(self.json_data)


class Task(models.Model):
    name = models.CharField(max_length=100, default='')
    message_name = models.CharField(max_length=100, blank=True)
    data_name = models.CharField(max_length=100)
    executions = models.PositiveIntegerField(default=0)
    cf_id = models.CharField(max_length=255, blank=True)

    # processInstance.getProcessDefinitionId() in activiti
    activiti_definition_id = models.CharField(max_length=255)
    # activiti_activity_id = models.CharField(max_length=255)
