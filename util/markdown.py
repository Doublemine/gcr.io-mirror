from .common import *
from .docker import *
import shutil
import fileinput
import glob
import os


def convert_to_array(namespace=None, dockerhub_name=None):
    result = load_jsond(f'{namespace}-synced.json', False)
    if result is None or not isinstance(result, list):
        Logger.info('can not load any data, result may not except value.')
        return None
    array = []
    array.append(['gcr registry', 'dockerhub', 'tags num'])
    for item in result:
        temp = []
        name = item['name']
        temp.append(name)
        docker_image = retag_image(name, dockerhub_name)
        temp.append(f'[{docker_image}](https://hub.docker.com/r/{docker_image})')
        temp.append(str(len(item['tags'])))
        array.append(temp)
        temp = None
    return array


# https://gist.github.com/m0neysha/219bad4b02d2008e0154
def make_markdown_table(array):
    """ Input: Python list with rows of table as lists
               First element as header.
        Output: String to put into a .md file

    Ex Input:
        [["Name", "Age", "Height"],
         ["Jake", 20, 5'10],
         ["Mary", 21, 5'7]]
    """

    markdown = "\n" + str("| ")

    for e in array[0]:
        to_add = " " + str(e) + str(" |")
        markdown += to_add
    markdown += "\n"

    markdown += '|'
    for _ in range(len(array[0])):
        markdown += str("-------------- | ")
    markdown += "\n"

    for entry in array[1:]:
        markdown += str("| ")
        for e in entry:
            to_add = str(e) + str(" | ")
            markdown += to_add
        markdown += "\n"

    return markdown + "\n"


def get_synced_namespace():
    synced_nm = []
    for file in os.listdir(get_dir()):
        if file.endswith("-synced.json"):
            synced_nm.append(file.replace('-synced.json', ''))
    return synced_nm


def do_export(username):
    nm = get_synced_namespace()
    if len(nm) <= 0:
        Logger.error("no yet synced namespace, skip...")
        return None
    for n in nm:
        generate_markdown(n, username)


def generate_markdown(namespace=None, username=None):
    if not os.path.exists(os.path.join(get_dir(), 'template.md')):
        Logger.error("can not found markdown template file, skip...")
        return None

    array = convert_to_array(namespace, username)
    if array is None:
        return None

    if os.path.exists(os.path.join(get_dir(), f'{namespace}.md')):
        os.remove(os.path.join(get_dir(), f'{namespace}.md'))
    shutil.copy2(os.path.join(get_dir(), 'template.md'), os.path.join(get_dir(), f'{namespace}.md'))

    array = convert_to_array(namespace, username)
    with fileinput.FileInput(os.path.join(get_dir(), f'{namespace}.md'), inplace=True) as file:
        for line in file:
            if '<title_place_holder>' in line:
                print(line.replace("<title_place_holder>", namespace), end='')
            elif '<image_num_place_holder>' in line:
                print(line.replace("<image_num_place_holder>", str(len(array)-1)), end='')

            else:
                print(line.replace("<synced_table_place_holder>", make_markdown_table(array)), end='')
