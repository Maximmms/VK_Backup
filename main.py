import json
import logging

from vk_api import VKApi
from ya_api import YANDEXApi
from settings import YATOKEN
from settings import VKTOKEN
from google_api import GDrive
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')

def convert_output(photos: dict[str, tuple[int, str, str]]) -> dict[str, str]:
    """
    Конвертирует словарь фотографий в словарь с уникальными именами файлов и URL.

    :param photos: Словарь, где ключи - ссылка URL, а значения - кортеж значений (Количество лайков, размер фото,
            дата добавления)
    :return: name_photo_dict: Словарь, в котором ключи Наименование файла, а значения URL картинки
    """
    state_dict = defaultdict(lambda: {'count': 0, 'first_date': None})
    name_photo_dict = {}
    json_list = list()

    for key, value in photos.items():
        likes = value[0]
        date_f = value[2]
        state = state_dict[likes]

        state['count'] += 1
        if state['first_date'] is None:
            state['first_date'] = date_f

        if state['count'] == 1:
            filename = f'{likes}.jpg'
        elif state['count'] == 2:
            filename = f"{likes}_{state['first_date']}.jpg"
        else:
            filename = f'{likes}_{state["first_date"]}_{state["count"] - 1}.jpg'

        name_photo_dict[filename] = key

    for key, value in name_photo_dict.items():
        json_list.append({"file_name": key, "size": photos.get(value)[1]})

    with open('result.json', 'w') as f:
        json.dump(json_list, f, indent=4)
    logging.info('\x1b[32mJSON файл result.json создан.\x1b[31m')

    return name_photo_dict

def extract_yandex(photo_dict: dict[str, tuple[int, str, str]], user_id: int, count: int):
    """
    Сохраняет фотографии на Яндекс.Диск.

    :param photo_dict: Словарь, где ключи - ссылка URL, а значения - кортеж значений (Количество лайков, размер фото,
            дата добавления)
    :param user_id: ID пользователя VK
    :param count: Количество фотографий, которые сохраняем
    """

    yandex = YANDEXApi(YATOKEN)
    files = convert_output(photo_dict)
    yandex.create_file(files, user_id, count)
    logging.info('\x1b[32mФотографии успешно загружены на Яндекс.Диск.\x1b[31m')

def extract_google(photo_dict: dict[str, tuple[int, str, str]], user_id: int, count: int):
    """
    Сохраняет фотографии на Google Drive

    :param photo_dict: Словарь, где ключи - ссылка URL, а значения - кортеж значений (Количество лайков, размер фото,
            дата добавления)
    :param user_id: ID пользователя VK
    :param count: Количество фотографий, которые сохраняем
    """

    gd = GDrive()
    files = convert_output(photo_dict)
    gd.create_file(files, user_id, count)
    logging.info('\x1b[32mФотографии успешно загружены на Google Drive.\x1b[31m')

if __name__ == '__main__':
    try:
        vk_user_id = int(input('Введите VK ID: ').strip())
        album_id = input('Введите откуда будем получать фотографии (Профиль или Все): ').strip().capitalize()
        count = input('Введите количество фотографий которые планируем сохранить: ').strip()

        if not count.isdigit():
            logging.error('Количество должно быть числом!')
            exit()

        count = int(count)
        if album_id not in {'Профиль', 'Все'}:
            logging.error('Неверное место получения фотографий!')
            exit()
        vk = VKApi(VKTOKEN)
        photo_dict = vk.get_photos(vk_user_id, int(count), album_id)
        logging.info(f'\x1b[32m{count} фотографий получено со страницы профиля.\x1b[31m')

        disk = input('Введите платформу на которую будем сохранять фотографии (Yandex или Google): ').strip().capitalize()
        match disk:
            case 'Yandex':
                extract_yandex(photo_dict, vk_user_id, count)
            case 'Google':
                extract_google(photo_dict, vk_user_id, count)
            case _:
                logging.error('Платформа не определена!')
    except Exception as e:
        logging.exception(f'Произошла ошибка: {e}')