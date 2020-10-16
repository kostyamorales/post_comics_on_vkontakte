import requests
from dotenv import load_dotenv
from os import getenv
from random import randint
from os import remove


def get_comics_quantity():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    quantity = response.json()['num']
    return quantity


def download_comic(quantity, filename):
    random_comic = randint(1, quantity)
    url = f'https://xkcd.com/{random_comic}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    answer = response.json()
    url_picture = answer['img']
    comment = answer['alt']
    picture_response = requests.get(url_picture)
    with open(filename, 'wb') as file:
        file.write(picture_response.content)
    return comment


def get_upload_url(parameters):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(url, params=parameters)
    response.raise_for_status()
    url = response.json()['response']['upload_url']
    return url


def upload_to_server(url):
    with open('comic.jpg', 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
        answer = response.json()
        parameter_photo = answer['photo']
        parameter_server = answer['server']
        parameter_hash = answer['hash']
        return parameter_photo, parameter_server, parameter_hash


def save_wall_photo(parameters, parameter_photo, parameter_server, parameter_hash):
    parameters['photo'] = parameter_photo
    parameters['server'] = parameter_server
    parameters['hash'] = parameter_hash
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    response = requests.get(url, params=parameters)
    response.raise_for_status()
    answer = response.json()['response'][0]
    owner_id = answer['owner_id']
    media_id = answer['id']
    attachments = f'photo{owner_id}_{media_id}'
    return attachments


def publish_entry(access_token, ver, group_id, comment, attachments):
    url = 'https://api.vk.com/method/wall.post'
    parameters = {
        'access_token': access_token,
        'v': ver,
        'owner_id': -group_id,
        'message': comment,
        'from_group': 1,
        'attachments': attachments
    }
    response = requests.post(url, params=parameters)
    response.raise_for_status()


def cleanse_directory(filename):
    remove(filename)


if __name__ == '__main__':
    load_dotenv()
    vk_group_id = int(getenv('VK_GROUP_ID'))
    vk_access_token = getenv('VK_ACCESS_TOKEN')
    vk_ver_api = 5.124
    params = {
        'access_token': vk_access_token,
        'v': vk_ver_api,
    }
    file_name = 'comic.jpg'
    try:
        comics_quantity = get_comics_quantity()
        comic_comment = download_comic(comics_quantity, file_name)
        upload_url = get_upload_url(params)
        param_photo, param_server, param_hash = upload_to_server(upload_url)
        param_attachments = save_wall_photo(params, param_photo, param_server, param_hash)
        publish_entry(vk_access_token, vk_ver_api, vk_group_id, comic_comment, param_attachments)
    finally:
        cleanse_directory(file_name)

