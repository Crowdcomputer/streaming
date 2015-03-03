import json
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse

from django.shortcuts import get_object_or_404


# Create your views here.
from rest_framework import viewsets, routers, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_200_OK
from croco.models import Task, TaskData
from croco.serializers import TaskSerializer
from croco.utils import process_events
from flower import Flower
from streaming.settings import API_KEY, CURRENT_URL


class TaskView(viewsets.ModelViewSet):
    """
    CRUD of Task, plus Start and Stop
    """
    queryset = Task.objects.all()
    model = Task
    serializer_class = TaskSerializer

    def __transform_list(self, data):
        data = json.loads(data)
        if not isinstance(data, list):
            return data
        else:
            res = dict()
            i=0
            for el in data:
                res["cc_data_"+str(i)] = el
                i+=1
            return res

    def __transform_results(self, input, output):
        # are both dictionaries
        # this combines data with unit_data
        # https://success.crowdflower.com/hc/en-us/articles/202703445-CrowdFlower-API-Integrating-with-the-API
        data = json.loads(input)
        out = json.loads(output)
        if not isinstance(data, dict):
            print "not a dict"
            return data
        else:
            return data.update(out)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        existing_task = Task.objects.filter(name=serializer.validated_data['name'],
                                            activiti_definition_id=serializer.validated_data['activiti_definition_id'])
        if not len(existing_task):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            # TODO PAVEL: update the webhook url here..
            from flower import Flower
            # update webhook_uri
            flower = Flower(API_KEY)
            webhook_settings = {
                    'send_judgments_webhook': True,
                    'webhook_uri': CURRENT_URL % str(serializer.data['id'])
                }
            u1 = flower.updateJob(serializer.data['cf_id'],webhook_settings)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(dict(id=existing_task[0].id), status=status.HTTP_200_OK)


    @detail_route(methods=['post'], url_path="start")
    def start(self, request, pk=None):
        # this is called by the BPMN
        task = get_object_or_404(Task, pk=pk)
        task.add_instances()
        # it should be always an object
        data = self.__transform_list(request.DATA['data'])
        flower = Flower(API_KEY)
        cf_task = flower.uploadUnit(task.cf_id, data)
        logging.debug(cf_task.text)
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
        task = get_object_or_404(Task, pk=pk)
        if request.method == "POST":

            # data from CF.
            # TODO: check if the signal is.
            # TODO: from here it seems that it's indentated
            # https://success.crowdflower.com/hc/en-us/articles/202703445-CrowdFlower-API-Integrating-with-the-API
            out_file = open("test.txt","w")
            out_file.write("%s" % json.dumps(request.DATA))
            out_file.close()
            judgments = Flower.parseWebhook(request.DATA)
            # we assume that only 1 at time is posted by CF
            # it should be like that.
            # we merge input and output..
            task.add_data(self.__transform_results(judgments[0]['unit_data'], judgments[0]['data']))
            return HttpResponse(status=HTTP_200_OK)
        else:
            return HttpResponse(json.dumps([td.get_data for td in task.data.all()]))


router = routers.DefaultRouter()
router.register(r'task', TaskView)