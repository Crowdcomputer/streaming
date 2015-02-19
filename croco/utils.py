import json
import logging

from requests.auth import HTTPBasicAuth
import requests


__author__ = 'Stefano Tranquillini <stefano.tranquillini@gmail.com>'

ACTIVITI_USERNAME = "kermit"
ACTIVITI_PASSWORD = "kermit"
ACTIVITI_URL = ""


# def deploy_process(filename, filedata):
#     files = {'file': (filename, filedata)}
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


def signal_message(id_execution, message, data_name, data):
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
    datapick = dict(action='messageEventReceived', messageName=message)
    variables = list()
    if not data:
        data = dict()
    variables.append(dict(name=data_name, value=data))
    datapick['variables'] = variables
    dumps = json.dumps(datapick)
    response_signal = requests.put(url, data=dumps, auth=HTTPBasicAuth(username, password))
    if response_signal.status_code == 204:
        return True
    else:
        return False


# def signal(id_execution, data=None):
#     username = ACTIVITI_USERNAME
#     password = ACTIVITI_PASSWORD
#     url = ACTIVITI_URL + "/runtime/executions/" + id_execution
#     datapick = dict(action='signal')
#     variables = []
#     # variables.append(createObject("executor_id",user.pk))
#     if data:
#         variables.append(dict(name="mydata", value=data, scope="global"))
#     datapick['variables'] = variables
#     # variables.append()
#     # datapick[] = task.parameters['receivers'] + "-pick"
#     dumps = json.dumps(datapick)
#     response_signal = requests.put(url, data=dumps, auth=HTTPBasicAuth(username, password))
#     if response_signal.status_code == 204:
#         return True
#     else:
#         return False


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
    # http://localhost:8080/activiti-rest/service/process-instance/149/signal
    url = ACTIVITI_URL + "/query/executions"
    dumps = json.dumps(dict(processDefinitionId=task.activiti_definition_id, messageEventSubscriptionName=task.message_name))
    response = requests.post(url, data=dumps, auth=HTTPBasicAuth(username, password))
    responsedata = response.json()['data']
    # if two users joins at the same time we are screwed
    if len(responsedata) > 0:
        # if message_name:
        return signal_message(str(responsedata[0]['id']), event.name, task.data_name,  data)
        # else:
        #     return signal(str(responsedata[0]['id']), str(len(responsedata)))
    return False


def process_events(task, data):
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
            for i in range(0, event.factor):
                send_event(task, event, data)
                logging.debug("Sent %s %s repeated %s" % (event.name, data, event.factor))
        else:
            # it's group
            datas = task.datas.all()
            # since we wnat them grouped, if the len is multipe of the group we send.
            if len(datas) % event.factor == 0:
                # takes the last factor elements.
                data = datas[-event.factor:]
                send_event(task, event, data)
                logging.debug("Sent %s %s grouped by %s" % (event.name, data, event.factor))


def send_event(task, event, data):
    # it should work also if't just 1 element
    signal_event_from_list(task,event,data)