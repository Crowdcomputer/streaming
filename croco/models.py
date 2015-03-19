# Create your models here.
import json
from django.db import models
from croco.utils import process_events

logger = logging.getLogger(__name__)

class Event(models.Model):
    EVENT_TYPE = (
        ('M', 'Multiply'),
        ('G', 'Group'),
    )
    type = models.CharField(max_length=1, choices=EVENT_TYPE)
    factor = models.PositiveSmallIntegerField()
    task = models.ForeignKey('Task', related_name='events')
    message_name = models.CharField(max_length=100, blank=True)



class TaskData(models.Model):
    json_data = models.TextField(default="{}")
    task = models.ForeignKey('Task', related_name='data')

    def set_data(self, data):
        if not isinstance(data, str):
            # expect a dict -> transform to json
            self.json_data = json.dumps(data)
        else:
            self.json_data = data

    def get_data(self):
        # always return a dict
        return json.loads(self.json_data)


class Task(models.Model):
    name = models.CharField(max_length=100, default='')
    data_name = models.CharField(max_length=100)
    executions = models.PositiveIntegerField(default=0)
    instances = models.PositiveIntegerField(default=0)

    cf_id = models.CharField(max_length=255, blank=True)

    # processInstance.getProcessDefinitionId() in activiti
    activiti_definition_id = models.CharField(max_length=255)
    # activiti_activity_id = models.CharField(max_length=255)

    def add_data(self, data):
        if isinstance(data,str):
            data = json.loads(data)
        self.add_executions()
        if isinstance(data, list):
            # TODO: what happens if there's a splitting and before starting the task?
            # data should is a list, we can iterate, do we want to?
            for datum in data:
                d = TaskData()
                d.set_data(datum)
                d.task = self
                d.save()
                # then we call
                process_events(self, d)
        else:
            d = TaskData()
            d.set_data(data)
            d.task = self
            d.save()
            # then we call
            data = self.data.all()
            logger.debug("data to process in the event %s", data)
            process_events(self,data)

    def add_instances(self):
        self.instances += 1
        self.save()

    def add_executions(self):
        self.executions += 1
        self.save()

    def completeness(self):
        if not self.instances:
            return 0.0
        return float(self.executions)/float(self.instances)