import json
import sys

__author__ = 'Stefano Tranquillini <stefano.tranquillini@gmail.com>'

import requests


def run_calls(id, data):
    print requests.post('http://localhost:8000/task/%s/results/' % id, json=json.dumps(data)).json()


if __name__ == "__main__":
    id = int(sys.argv[1])
    for i in range(10):
        run_calls(id, dict(data=i))
        if i+1 % 2 == 0:
            run_calls(id+1,dict(data=10+i))