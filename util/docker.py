from .common import Logger
import docker


def pull_image_then_retag(docker_client=None, repository=None, tag='latest', retag_repository=None):
    """
    pull image by specific repository and tag.
    return True if tag and pull success.
    """
    try:
        Logger.debug(f"ready to pull the image {repository}:{tag}")
        image = docker_client.images.pull(repository, tag)
        Logger.info(f"pull the image {image.attrs['RepoTags'][0]} completed,ready to re-tag.")
        return image.tag(retag_repository, tag)
    except docker.errors.APIError as error:
        Logger.error(error)
        return False


def push_image(docker_client=None, repository=None, tag='latest'):
    try:
        for line in docker_client.images.push(repository, tag=tag, stream=True, decode=True):
            format_output(line)
        return True
    except docker.errors.APIError as error:
        Logger.error(error)
        return False


def delete_pushed_image(docker_client=None, repository=None, tag='latest'):
    try:
        docker_client.images.remove(f"{repository}:{tag}", True, False)
        return True
    except docker.errors.APIError as error:
        Logger.error(error)
        return False


def retag_image(gcr_image_repository=None, dockerhub_username=None):
    """
    re-tag the gcr.io image to dockerhub's name.
    """
    temp = gcr_image_repository.replace('gcr.io/', '')
    temp = temp.replace('/', '.')
    return f"{dockerhub_username}/{temp}"


def format_output(output):
    try:
        if not isinstance(output, dict):
            return
        if 'aux' in output:
            Logger.info(output['aux']['Digest'])
            return
        if 'digest' in output:
            Logger.info(output['digest'])
            return
        if 'progress' in output:
            Logger.info(output['progress'])
            return
        else:
            return
    except Exception:
        Logger.info("Process log parse failed.")
        return
