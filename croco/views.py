import json
import logging
from django.http.response import HttpResponse

from django.shortcuts import get_object_or_404


# Create your views here.
from rest_framework import viewsets, routers
from rest_framework.decorators import detail_route
from rest_framework.status import HTTP_204_NO_CONTENT
from croco.models import Task, TaskData
from croco.serializers import TaskSerializer
from croco.utils import process_events


class TaskView(viewsets.ModelViewSet):
    """
    CRUD of Task, plus Start and Stop
    """
    queryset = Task.objects.all()
    model = Task
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        serializer.save()
        #TODO: call CF to instantiate the task

    @detail_route(methods=['post', 'get'], url_path="results")
    def post_result(self, request, pk=None):
        """
        To post results, this is the function that CF (or middleware) should call.
        POST {} /task/:id:/results/ (note the final /) . pass a json.

        :param request:
        :param pk:
        :return:
        """
        task = get_object_or_404(Task,pk=pk)
        if request.method == "POST":
            d = TaskData(task=task)
            d.set_data(request.DATA)
            d.save()
            # check the results
            process_events(task, d)
            return HttpResponse(status=HTTP_204_NO_CONTENT)
        else:
            return HttpResponse(json.dumps([td.get_data for td in task.data.all()]))


router = routers.DefaultRouter()
router.register(r'task', TaskView)