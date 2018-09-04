import requests
import sys
import os
import re
import docker
import json
from argparse import ArgumentParser
import random
import datetime
import inspect
from functools import wraps
import signal
from termcolor import colored
import logging
import time
from util import *


class TravisTimeoutException(Exception):
    pass


def travis_timeout_handler(signum, frame):
    Logger.error("timeout for tavis, start store data...")
    raise TravisTimeoutException("Travis timeout")


def sync(docker_client=None, gcr_image=None, dockerhub_name=None):
    if gcr_image['tags'] is None or not 'tags' in gcr_image or len(gcr_image['tags']) <= 0:
        Logger.info("Skip tag...")
        return
    gcr_tag_list = gcr_image['tags']
    gcr_image_repository = gcr_image['name']
    dockerhub_repository = retag_image(gcr_image_repository, dockerhub_name)
    success_tag_list = []
    try:
        for tag in gcr_tag_list:
            result = pull_image_then_retag(docker_client, gcr_image_repository, tag, dockerhub_repository)
            if result:
                Logger.success(f"pull and tag image of tag {gcr_image_repository}:{tag} success")
                result = push_image(docker_client, dockerhub_repository, tag)
                if not result:
                    Logger.error(f"push image error for {dockerhub_repository}:{tag}")
                else:
                    success_tag_list.append(tag)
                    Logger.success(f"push {dockerhub_repository}:{tag} completed.")
            else:
                Logger.error(f"pull and tag image of tag {gcr_image_repository}:{tag} failed")
        for tag in gcr_tag_list:
            Logger.info(f"ready for delete docker image {dockerhub_repository}:{tag}")
            delete_pushed_image(docker_client, dockerhub_repository, tag)
            Logger.info(f"ready for delete docker image {gcr_image_repository}:{tag}")
            delete_pushed_image(docker_client, gcr_image_repository, tag)

        total = len(gcr_tag_list)
        success = len(success_tag_list)
        Logger.error(" total num: {} success sync num: {} ".format(total, success))
        return {'name': gcr_image_repository, 'tags': success_tag_list, 'interrupt': False}
    except TravisTimeoutException as error:
        Logger.error(error)
        total = len(gcr_tag_list)
        success = len(success_tag_list)
        Logger.error("occur travis timeout warning, interrupt sync. total num: {} success sync num: {} ".format(total, success))
        return {'name': gcr_image_repository, 'tags': success_tag_list, 'interrupt': True}


def sync_to_dockerhub(docker_client=None, namespace=None, username=None):
    synced_list = []
    image_list = fetch_image_list_by_namespace(namespace=namespace)
    completed = load_jsond(f'{namespace}-synced.json', False)
    try:
        for image in image_list:
            gcr_image_dict = fetch_image_tag(namespace, image)
            gcr_image_dict = filter_unsynced_image_tags(gcr_image_dict, completed)
            Logger.debug('fetch special image list is {}'.format(str(gcr_image_dict)))
            synced_image = sync(docker_client, gcr_image_dict, username)
            if synced_image is not None:
                if synced_image['interrupt']:
                    synced_image.pop('interrupt', None)
                    if 'tags' in synced_image and len(synced_image['tags']) > 0:
                        synced_list.append(synced_image)
                    break
                else:
                    synced_image.pop('interrupt', None)
                    if 'tags' in synced_image and len(synced_image['tags']) > 0:
                        synced_list.append(synced_image)
            else:
                Logger.info('sync funcation return None, maybe sync all tag.')

        if len(synced_list) > 0:
            Logger.info("update synced image data, synced_list: {}".format(str(synced_list)))
            update_synced_list(synced_list, namespace)

    except TravisTimeoutException:
        if len(synced_list) > 0:
            Logger.error("occur travis timeout, update synced image data, synced_list: {}".format(str(synced_list)))
            update_synced_list(synced_list, namespace)


def cli_parser():
    parser = ArgumentParser(description='Pull image from gcr.io then re-tag and push to docker hub, You must specific the env var named GCR_COOKIE')

    parser.add_argument('-n', '--namespace', help='specific namespace of gcr.io registry', default='google-containers', type=str, required=False, dest='namespace')

    parser.add_argument('-un', '--username', help='the dockerhub username', default=None, type=str, required=True, dest='username')

    parser.add_argument('-pwd', '--password', help='the dockerhub password', default=None, type=str, required=False, dest='password')

    parser.add_argument('--markdown-only', help='generat markdown file', action='store_true', required=False, dest='markdown')

    args = parser.parse_args()
    return args


def main():
    cli_vars = cli_parser()
    client = docker.from_env()

    if cli_vars.markdown:
        Logger.info("execute markdown table export...")
        do_export(cli_vars.username)
        return

    Logger.debug('ready for docker login...')
    login_result = client.login(username=cli_vars.username, password=cli_vars.password, registry='https://index.docker.io/v1/')
    Logger.info('docker login response:'+login_result['Status'])

    signal.signal(signal.SIGALRM, travis_timeout_handler)
    alarm_sec = int(os.getenv('ALARM_SEC', -1))
    if alarm_sec == -1:
        Logger.debug("can not get alarm sec use default time 2400s.")
        alarm_sec = 60*40
    signal.alarm(alarm_sec)
    sync_to_dockerhub(client, cli_vars.namespace, cli_vars.username)


if __name__ == '__main__':
    main()
