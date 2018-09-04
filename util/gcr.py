import os
import requests
import re
from .common import Logger


def fetch_image_list_by_namespace(namespace=None):
    """
    fetch repository by specific namespace
    """
    url = "https://console.cloud.google.com/m/gcr/entities/list"
    payload = f'["{namespace}",null,null,[]]'
    headers = {
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        'cookie': os.getenv('GCR_COOKIE'),
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        'content-type': "application/json;charset=UTF-8",
        'accept': "application/json, text/plain, */*",
        'Cache-Control': "no-cache"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    pattern = re.compile(r'"[a-z0-9-]{0,}"', flags=8)
    rough_list = pattern.findall(response.text)
    image_list = []
    for item in rough_list:
        image_list.append(item.replace('"', ''))
    return list(set(image_list))


def fetch_image_tag(namespace=None, image_name=None):
    """
    fetch all image tags by specific repository
    """
    url = f"https://gcr.io/v2/{namespace}/{image_name}/tags/list"
    Logger.debug('request image tag uri:{}'.format(url))
    headers = {
        'Cache-Control': 'no-cache',
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    }
    response = requests.request("GET", url, headers=headers)
    tag_list = response.json()['tags']
    tag_list = filter_unrelease_tags(tag_list)
    Logger.info("filter un-release tags list:{}".format(str(tag_list)))
    name = response.json()['name']
    return {'name': f"gcr.io/{name}", 'tags': tag_list}


def fetch_undo_list(unfetch_list, namespace=None):
    undo_list = []
    for item in unfetch_list:
        gcr_image_list = fetch_image_tag(namespace, item)
        undo_list.append(gcr_image_list)
    return undo_list


def filter_unrelease_tags(tags=None):
    if tags is None or len(tags) <= 0:
        return
    pattern = re.compile(r'(rc.*|alpha.*|beta.*|experimental.*)$', flags=8)
    temp = []
    for item in tags:
        if pattern.search(item) is not None:
            temp.append(item)
    return list(set(set(tags)-set(temp)))
