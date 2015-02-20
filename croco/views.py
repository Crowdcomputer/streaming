import json
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse

from django.shortcuts import get_object_or_404


# Create your views here.
from rest_framework import viewsets, routers, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        existing_task = Task.objects.filter(name=serializer.validated_data['name'],
                                            activiti_definition_id=serializer.validated_data['activiti_definition_id'])
        if not len(existing_task):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            # TODO PAVEL: update the webhook url here..
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(dict(pk=existing_task[0].pk), status=status.HTTP_200_OK)


    @detail_route(methods=['post'], url_path="start")
    def start(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        task.add_instances()
        data = request.DATA
#       TODO PAVEL: call crowdflower,
        return HttpResponse(status=HTTP_204_NO_CONTENT)


    @detail_route(methods=['post', 'get'], url_path="results")
    def results(self, request, pk=None):
        """
        To post results, this is the function that CF (or middleware) should call.
        POST {} /task/:id:/results/ (note the final /) . pass a json.

        :param request:
        :param pk:
        :return:
        """
        task = get_object_or_404(Task,pk=pk)
        if request.method == "POST":
            task.add_data(request.DATA)
            return HttpResponse(status=HTTP_204_NO_CONTENT)
        else:
            return HttpResponse(json.dumps([td.get_data for td in task.data.all()]))


router = routers.DefaultRouter()
router.register(r'task', TaskView)