import requests
from dotenv import load_dotenv
from os import getenv
from random import randint
from os import remove


def get_comics_quantity():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comics_quantity = response.json()['num']
    return comics_quantity


def download_comic(comics_quantity, filename):
    random_comic = randint(1, comics_quantity)
    url = f'https://xkcd.com/{random_comic}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    url_picture = response.json()['img']
    comment = response.json()['alt']
    picture_response = requests.get(url_picture)
    with open(filename, 'wb') as file:
        file.write(picture_response.content)
    return comment


def get_upload_url(params):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(url, params=params)
    response.raise_for_status()
    upload_url = response.json()['response']['upload_url']
    return upload_url


def upload_to_server(upload_url):
    new_params = {}
    with open('comic.jpg', 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
        new_params['photo'] = response.json()['photo']
        new_params['server'] = response.json()['server']
        new_params['hash'] = response.json()['hash']
        return new_params


def save_wall_photo(params, new_params):
    new_params.update(params)
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    response = requests.get(url, params=new_params)
    response.raise_for_status()
    answer = response.json()['response'][0]
    owner_id = answer['owner_id']
    media_id = answer['id']
    attachments = f'photo{owner_id}_{media_id}'
    return attachments


def publish_entry(access_token, ver, group_id, comment, attachments):
    url = 'https://api.vk.com/method/wall.post'  # Публикация записи в группе
    params = {
        'access_token': access_token,
        'v': ver,
        'owner_id': -group_id,
        'message': comment,
        'from_group': 1,
        'attachments': attachments
    }
    response = requests.post(url, params=params)
    response.raise_for_status()


def cleanse_directory(filename):
    remove(filename)


def publish_comic(group_id, access_token, ver_api):
    params = {
        'access_token': vk_access_token,
        'v': ver_api,
    }
    file_name = 'comic.jpg'
    comics_quantity = get_comics_quantity()
    comic_comment = download_comic(comics_quantity, file_name)
    upload_url = get_upload_url(params)
    new_params = upload_to_server(upload_url)
    attachments = save_wall_photo(params, new_params)
    publish_entry(access_token, ver_api, group_id, comic_comment, attachments)
    cleanse_directory(file_name)


if __name__ == '__main__':
    load_dotenv()
    vk_group_id = int(getenv('VK_GROUP_ID'))
    vk_access_token = getenv('VK_ACCESS_TOKEN')
    vk_ver_api = 5.124
    publish_comic(vk_group_id, vk_access_token, vk_ver_api)
