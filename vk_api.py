import requests

from datetime import datetime


class VKApi:
    VK_API_BASE_URL = 'https://api.vk.ru/method/'

    def __init__(self, token):
        """

        :param token: Токен VK для доступа к VK
        """
        self.token = token
        self.params = {
            'access_token': self.token,
            'v': '5.199',
        }

    def get_photos(self, user_id, count: int=5, album: str='Профиль'):
        """

        :param user_id: ID пользователя VK
        :param count: Количество фотографий
        :param album: Альбон из которого получаем фотографии
        :return: Словарь, где ключи - ссылка URL, а значения - кортеж значений (Количество лайков, размер фото,
            дата добавления)
        """
        ph_url_lst = dict()
        if album == 'Профиль':
            album_id = 'profile'
            api_method = 'photos.get'
        else:
            album_id = 'saved'
            count += 1
            api_method = 'photos.getAll'
        url = f'{self.VK_API_BASE_URL}{api_method}'
        params = {
            'owner_id': user_id,
            'count': count,
            'album_id': album_id,
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