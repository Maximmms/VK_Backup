import requests

from datetime import datetime


class VKApi:
    VK_API_BASE_URL = 'https://api.vk.ru/method/'

    def __init__(self, token):

        self.token = token
        self.params = {
            'access_token': self.token,
            'v': '5.199',
        }

    def get_photos(self, user_id, count: int=5):
        ph_url_lst = dict()
        url = f'{self.VK_API_BASE_URL}photos.get'
        params = {
            'owner_id': user_id,
            'count': count,
            'album_id': 'profile',
            'extended': 1,
        }
        params.update(self.params)
        response = requests.get(url, params=params)
        for item in response.json()['response']['items']:
            key = item['sizes'][-1]['url']
            likes = item['likes']['count']
            size_type = item['sizes'][-1]['type']
            photo_date = datetime.utcfromtimestamp(item['date']).strftime('%d-%m-%Y')
            ph_url_lst.update({key: (likes, size_type, photo_date)})

        return ph_url_lst

    def get_all_photos(self, user_id, count: int = 5):

        ph_url_lst = dict()
        url = f'{self.VK_API_BASE_URL}photos.getAll'
        params = {
            'owner_id': user_id,
            'count': count + 1,
            'album_id': 'saved',
            'extended': 1,
        }
        params.update(self.params)
        response = requests.get(url, params=params)
        for item in response.json()['response']['items']:
            key = item['sizes'][-1]['url']
            likes = item['likes']['count']
            size_type = item['sizes'][-1]['type']
            photo_date = datetime.utcfromtimestamp(item['date']).strftime('%d-%m-%Y')
            ph_url_lst.update({key: (likes, size_type, photo_date)})

        return ph_url_lst