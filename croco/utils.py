import json
import logging

from requests.auth import HTTPBasicAuth
import requests
from streaming.settings import ACTIVITI_USERNAME, ACTIVITI_PASSWORD, ACTIVITI_URL


__author__ = 'Stefano Tranquillini <stefano.tranquillini@gmail.com>'

# ACTIVITI_USERNAME = "kermit"
# ACTIVITI_PASSWORD = "kermit"
# ACTIVITI_URL = "http://localhost:8080/activiti-rest/service"

logger = logging.getLogger(__name__)

# def deploy_process(filename, filedata):
# files = {'file': (filename, filedata)}
#     url = ACTIVITI_URL + "/repository/deployments"
#     response = requests.post(url, files=files, auth=HTTPBasicAuth(ACTIVITI_USERNAME, ACTIVITI_PASSWORD))
#     if response.status_code == 201:
#         return files
#     else:
#         raise Exception("Something went wrong while deploying the file %s" % response.text)

#
# def start_process(process_id, data):
#     url = ACTIVITI_URL + "/runtime/process-instances"
#     response = requests.post(url, data=json.dumps(data),
#                              auth=HTTPBasicAuth(ACTIVITI_USERNAME, ACTIVITI_PASSWORD))
#     jsonresp = response.json()
#     processInstanceId = jsonresp.get("id")
#     processDefinition = jsonresp.get("processDefinitionId")
#     return processInstanceId, processDefinition


def signal_message(id_execution, data_name, data):
    """
    Signals a message for the process

    :param id_execution:
    :param message:
    :param data_name:
    :param data:
    :return:
    """
    username = ACTIVITI_USERNAME
    password = ACTIVITI_PASSWORD
    url = ACTIVITI_URL + "/runtime/executions/" + id_execution
    datapick = dict(action='signal')
    variables = []
    # variables.append(createObject("executor_id",user.pk))
    if data:
        variables.append(dict(name=data_name, value=data))
    datapick['variables'] = variables
    # variables.append()
    # datapick[] = task.parameters['receivers'] + "-pick"
    dumps = json.dumps(datapick)
    logger.debug("dumping %s" % dumps)
    response_signal = requests.put(
        url, data=dumps, auth=HTTPBasicAuth(username, password))
    if response_signal.status_code == 204:
        logger.debug("Signal ok")
        return True
    else:
        logger.error("Error %s" % response_signal.text)
        return False



def signal_event_from_list(task, event, data):
    """
    Search in the process what are the activity waiting for the message.
    Once found, takes the first and send the data

    :param task:
    :param event:
    :param data:
    :return:
    """
    username = ACTIVITI_USERNAME
    password = ACTIVITI_PASSWORD
    url = ACTIVITI_URL + "/query/executions"
    dumps = json.dumps(
        dict(processDefinitionId=task.activiti_definition_id, messageEventSubscriptionName=event.message_name))
    response = requests.post(url, data=dumps, auth=HTTPBasicAuth(username, password))
    responsedata = response.json()['data']
    # if two users joins at the same time we are screwed
    if len(responsedata) > 0:
        # if message_name:
        return signal_message(str(responsedata[0]['id']), task.data_name, data)
        # else:
        #     return signal(str(responsedata[0]['id']), str(len(responsedata)))
    return False


def process_events(task, task_data):
    """
    Checks all the events and calls the events.
    It may take a while.

    :param task:
    :param data:
    :return:
    """
    for event in task.events.all():
        if event.type == "M":
            # it's multiply, then send the event many times
            data = task_data
            last_data = data[len(data) - 1]
            logger.debug("sending %s %s of %s",(event.message_name, event.factor, last_data.get_data()))
            for i in range(event.factor):
                send_event(task, event, [last_data.get_data()])
        else:
            # it's group
            datas = task_data
            # since we wnat them grouped, if the len is multipe of the group we send.

            if len(datas) > 0 and len(datas) % event.factor == 0:
                # takes the last factor elements.
                # BUG?: negative index here does not work
                index = len(datas) - event.factor
                t_data = datas[index:]
                j_data = []
                for d in t_data:
                    j_data.append(d.get_data())
                # print "%s %s" % (data, da[-event.factor:])
                logger.debug("sending %s %s of %s",(event.message_name, event.factor, j_data))
                send_event(task, event, j_data)
                # print ("Sent %s %s grouped by %s" % (event.message_name,  data, event.factor))


def send_event(task, event, data):
    # TODO: re-enable this
    # print "send event %s (%s:%s) data  %s" % (event.message_name, event.factor, event.type, data)
    # it should work also if't just 1 element
    logger.debug("Event in charge is %s: %s" % (event.message_name, data))
    # signal_event_from_list(task, event, data)
