from termcolor import colored
import logging
import time
import os
import json
from pathlib import Path
import shutil


class Logger:
    def __init__(self):
        self.__logger = logging.getLogger()
        Logger.mkdir_if_not_exist('logs')
        __file_name = 'logs/' + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'
        __handler = logging.FileHandler(filename=__file_name, mode='a', encoding='utf-8')
        __formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        __handler.setFormatter(__formatter)
        self.__logger.addHandler(__handler)
        self.__logger.setLevel(logging.DEBUG)

    def d(self, msg, *args, **kwargs):
        self.__logger.debug(msg, *args, **kwargs)

    def i(self, msg, *args, **kwargs):
        self.__logger.info(msg, *args, **kwargs)

    def w(self, msg, *args, **kwargs):
        self.__logger.warning(msg, *args, **kwargs)

    def e(self, msg, *args, **kwargs):
        self.__logger.error(msg, *args, **kwargs)

    @staticmethod
    def info(msg):
        print(colored(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ":" + str(msg), 'yellow'))

    @staticmethod
    def success(msg):
        print(colored(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ":" + str(msg), 'green'))

    @staticmethod
    def error(msg):
        print(colored(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ":" + str(msg), 'red'))

    @staticmethod
    def debug(msg):
        print(colored(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ":" + str(msg), 'blue'))

    @staticmethod
    def mkdir_if_not_exist(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)


def filter_unsynced_image_tags(fetched_dict=None, synced_list=None):
    """
    sample data of fetched_list :
        {
        "name": "gcr.io/kubernetes-helm/tiller",
        "tags": [
            "canary",
            "test-release",
            "v2.0.0",
                ]
        }
    """
    if not isinstance(fetched_dict, dict) or not isinstance(synced_list, list):
        Logger.error("filter unsynced list cause some unexcept status, the fetched_dict type is: {}, synced_list type is:{}".format(str(type(fetched_dict)), str(type(synced_list))))
        return fetched_dict
    for do_item in synced_list:
        if not isinstance(do_item, dict):
            continue

        if do_item['name'] == fetched_dict['name']:
            no_duplicate_tags = remove_duplicates_item(do_item['tags'], fetched_dict['tags'])
            return {'name': fetched_dict['name'], 'tags': no_duplicate_tags}
    Logger.info("can not match the same dict, direct return fetched_list, fetched_dict's name: {}".format(str(fetched_dict['name'])))
    return {'name': fetched_dict['name'], 'tags': fetched_dict['tags']}


def remove_duplicates_item(fl=None, sl=None):
    if not isinstance(fl, list) and not isinstance(sl, list):
        return sl
    for fli in fl:
        if fli in sl:
            sl.remove(fli)
    return sl


def add_synced_image_tags(success_list=None, synced_list=None):
    if not isinstance(success_list, list) or not isinstance(synced_list, list):
        Logger.error("add synced image error, return success_list directly.")
        return success_list
    temp = []
    combin_synced = []
    combin_success = []
    for s in synced_list:
        for i in success_list:
            if s['name'] == i['name']:
                temp.append({'name': s['name'], 'tags': list(set(s['tags']+i['tags']))})
                combin_success.append(i)
                combin_synced.append(s)

    for i in range(len(combin_synced)):
        if combin_success[i] in success_list:
            success_list.remove(combin_success[i])
        if combin_synced[i] in synced_list:
            synced_list.remove(combin_synced[i])

    temp = temp+synced_list+success_list
    return remove_duplicate(temp)


def load_jsond(filename, load_after_delete=True, rm_dupliacate=True):
    if not os.path.exists(os.path.join(get_dir(), filename)):
        Logger.error("[load_jsond] can not found the target file of path: {}".format(filename))
        return None
    cache = open(os.path.join(get_dir(), filename), "r")
    undo_task = json.load(cache)
    cache.close()
    if load_after_delete:
        os.remove(os.path.join(get_dir(), filename))
    if rm_dupliacate:
        return remove_duplicate(undo_task)
    return undo_task


def save_jsond(filename, data=None, overwrite=True):
    if overwrite and os.path.exists(os.path.join(get_dir(), filename)):
        os.remove(os.path.join(get_dir(), filename))
    file = open(os.path.join(get_dir(), filename), "w")
    json.dump(data, file)
    file.close()


def update_synced_list(synced_list=None, namespace=None):
    synced = load_jsond(f'{namespace}-synced.json')
    save_jsond(f'{namespace}-synced.json', add_synced_image_tags(synced_list, synced))


def get_dir():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return Path(dir_path).parent


def remove_duplicate(data_list):
    if data_list is None or len(data_list) <= 0:
        return data_list
    temp = []
    for item in data_list:
        if item not in temp:
            temp.append(item)
    return temp


def show_disk():
    try:
        total, used, free = shutil.disk_usage(r'/var/lib/docker')
        Logger.info("Total: {}GB, Used: {} GB, Free: {}GB".format(str((total // (2**30))), str((used // (2**30))), str((free // (2**30)))))
    except Exception:
        return


def update_trigger(trigger=False, force=False):
    synced = load_jsond('trigger.json', False, False)
    if synced is None:
        synced = {'trigger': trigger}

    if isinstance(synced, list):
        synced = synced[0]

    if force:
        synced['trigger'] = trigger
    else:
        if not synced['trigger']:
            synced['trigger'] = trigger

    save_jsond('trigger.json', synced, True)


def read_trigger():
    synced = load_jsond('trigger.json')
    if synced is None:
        return True
    else:
        if 'trigger' in synced:
            return synced['trigger']
        else:
            return True
