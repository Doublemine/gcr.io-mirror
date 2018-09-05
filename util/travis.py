import requests
from .common import *
import os
import json


def trigger_build():
    USER_NAME = os.getenv('USERNAME')
    REPO_NAME = os.getenv('REPO_NAME')
    TOKEN = os.getenv('TRAVIS_TOKEN')
    BRANCH = os.getenv('T_BRANCH')
    url = f"https://api.travis-ci.org/repo/{USER_NAME}%2F{REPO_NAME}/requests"
    headers = {
        'Travis-API-Version': "3",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
        'Content-Type': "application/json",
        'Accept': "application/json",
        'Authorization': f"token {TOKEN}",
        'Cache-Control': "no-cache",
    }

    payload = {
        'request': {
            'branch': BRANCH
        }
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

    if response.ok:
        Logger.success("Trigger build success, detail is: {}".format(response.text))
    else:
        Logger.error("Trigger build failed, detail is: {}".format(response.text))
