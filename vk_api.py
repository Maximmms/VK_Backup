import logging

import requests

from datetime import datetime

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)  # Создаем отдельный логгер для класса


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
        Получение фотографий по запросу

        :param user_id: ID пользователя VK
        :param count: Количество фотографий
        :param album: Альбон из которого получаем фотографии
        :return: Словарь, где ключи - ссылка URL, а значения - кортеж значений (Количество лайков, размер фото,
            дата добавления)
        """
        logger.info(f"\x1b[33mЗапрос фотографий для пользователя ID {user_id}, альбом: {album}, количество: {count}\x1b[31m")

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

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Проверяем успешность запроса
            logger.info(f"\x1b[33mУспешный запрос: {response.url}\x1b[31m")

            items = response.json().get('response', {}).get('items', [])
            logger.debug(f"\x1b[33mПолучено {len(items)} элементов.\x1b[31m")

            ph_url_lst = {
                item['sizes'][-1]['url']: (
                    item['likes']['count'],
                    item['sizes'][-1]['type'],
                    datetime.utcfromtimestamp(item['date']).strftime('%d-%m-%Y')
                )
                for item in items
            }

            logger.info(f"\x1b[33mОбработано {len(ph_url_lst)} фотографий.\x1b[31m")
            return ph_url_lst

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе: {e}")
            return {}
        except ValueError:
            logger.error("Ошибка при обработке ответа JSON.")
            return {}