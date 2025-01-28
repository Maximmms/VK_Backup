import logging

import requests
import json
import io
import time

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)  # Создаем отдельный логгер для класса

class GDrive:

    def __init__(self):
        try:
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()
            self.drive = GoogleDrive(gauth)
            self.access_token = gauth.attr['credentials'].access_token
            logging.info("\x1b[32mУспешная авторизация в Google Drive.\x1b[31m")
        except Exception as e:
            logging.error(f"Ошибка при авторизации в Google Drive: {e}")
            raise

    def _create_folder(self, folder_name, root_folder_id = 'root'):
        """
        Создание папки на Диске

        :param folder_name: Имя папки
        :param root_folder_id: ID корневой папки каталога
        """
        file_metadata = {
            'title': folder_name,
            'parents': [root_folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }

        try:
            folder = self.drive.CreateFile(file_metadata)
            folder.Upload()
            logging.info(f'\x1b[32mПапка "{folder_name}" успешно создана.\x1b[31m')
        except Exception as e:
            logging.error(f'Не удалось создать папку "{folder_name}": {e}')


    def _check_folder_exists(self, item_name, folder_id = 'root'):
        """
        Проверка наличия папки на диске

        :param item_name: Имя файла.папки для проверки
        :param folder_id: ID корневой папки каталога
        :return: NONE если папки не существует и ID папки, если она есть
        """
        lst =self.drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
        for item in lst:
            if item['title'] == str(item_name):
                return item['id']
            else:
                continue

    def create_file(self, photos, user_id, count):
        """
        Создание файла на диске в выбранной папке

        :param photos: Словарь, где ключи - наименование файлов, а значения URL ссылка на картинку
        :param user_id: ID страницы в VK - используется как название папки для сохранения фотографий
        :param count: Количество сохраняемых фотографий
        """
        folder_id = self._check_folder_exists(user_id)
        if folder_id is None:
            self._create_folder(user_id)
            logging.info(f'\x1b[32mПапка "{user_id}" успешно создана.\x1b[31m')
            folder_id = self._check_folder_exists(user_id)

        for f_name, f_url in list(photos.items())[:count]:
            time.sleep(0.5)
            file_id = self._check_folder_exists(f_name, folder_id)
            if file_id is None:
                try:
                    metadata = {"name": f_name, "parents": [folder_id]}
                    file = {
                        "data": ('metadata', json.dumps(metadata), "application/json"),
                        "file": io.BytesIO(requests.get(f_url).content)
                    }
                    response = requests.post(
                        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true",
                        headers={"Authorization": f"Bearer {self.access_token}"},
                        files=file
                    )
                    if response.status_code == 200:
                        logging.info(f'\x1b[32mФайл "{f_name}" успешно создан.\x1b[31m')
                    else:
                        logging.warning(f'Не удалось создать файл "{f_name}". Код ответа: {response.status_code}')
                except Exception as e:
                    logging.error(f'Ошибка при создании файла "{f_name}": {e}')
            else:
                logging.info(f'Файл "{f_name}" уже существует.')