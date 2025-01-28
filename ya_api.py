import logging
import requests
import time

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)  # Создаем отдельный логгер для класса

class YANDEXApi:


    YA_API_BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, token):
        """
        Инициализация клиента Yandex Disk API

        :param token: Токен для доступа к Yandex
        """
        self.token = token

    def _get_common_params(self):
        """
        Получение общих заголовков для запросов.

        :return: Заголовки с авторизацией.
        """
        return {
            'Authorization': f'OAuth {self.token}',
        }

    def _get_files(self, user_id):
        """
        Получения спика файлов в выбранной папке

        :param user_id: ID страницы в VK - используется как название папки для сохранения фотографий
        :return: Список файлов в папке user_id
        """
        name_lst = []
        headers = self._get_common_params()
        params = {'path': user_id, 'limit': 100}
        url = f"{self.YA_API_BASE_URL}"
        if requests.get(url, headers=headers, params=params).status_code != 404:
            files = requests.get(url, headers=headers, params=params).json()['_embedded']['items']
            for item in files:
                name_lst.append(item['name'])
            return name_lst
        else:
            return []

    def create_file(self, photos, user_id, count: int):
        """
        Создание файла на диске

        :param photos: Словарь, где ключи - наименование файлов, а значения URL ссылка на картинку
        :param user_id: ID страницы в VK - используется как название папки для сохранения фотографий
        :param count: Количество сохраняемых фотографий
        """

        files = self._get_files(user_id)
        headers = self._get_common_params()
        url = f"{self.YA_API_BASE_URL}/upload"
        folder_params = {'path': user_id}
        requests.put(self.YA_API_BASE_URL, headers=headers, params=folder_params)

        for f_name, f_url in photos.items():
            time.sleep(0.5)
            if f_name not in files:
                file_params = {'path': f'{user_id}/{f_name}', 'url': f_url}
                file = requests.post(url, headers=headers, params=file_params)
                if file.status_code == 202:
                    logging.info(f'\x1b[32mФайл "{f_name}" успешно создан.\x1b[31m')
                else:
                    logger.warning(f"Не удалось создать файл {user_id}/{f_name}.")
            else:
                logger.info(f"\x1b[33mФайл {f_name} уже существует в папке {user_id}.\x1b[31m")