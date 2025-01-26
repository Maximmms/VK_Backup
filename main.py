import json

from vk_api import VKApi
from ya_api import YANDEXApi
from settings import YATOKEN
from settings import VKTOKEN
from google_api import GDrive
from collections import defaultdict




def convert_output(photos: dict):
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
        f.close()

    return name_photo_dict

def extract_yandex(photo_dict, user_id, count: int):
    yandex = YANDEXApi(YATOKEN)
    yandex.create_file(convert_output(photo_dict), user_id, count)
    pass

def extract_google(photo_dict, user_id, count: int):
    gd = GDrive()
    gd.create_file(convert_output(photo_dict), user_id, count)
    pass



if __name__ == '__main__':
    vk_user_id = input('Введите VK ID: ')
    # vk_user_id = 14931219  # идентификатор пользователя vk
    vk = VKApi(VKTOKEN)

    album_id = input('Введите откуда будем получать фотографии (Профиль или Все): ')
    count = input('Введите количество фотографий которые планируем сохранить: ')
    if album_id == 'Профиль':
        photo_dict = vk.get_photos(vk_user_id , int(count))
        print(f'{count} фотографий получено со страницы профиля!')
    elif album_id == 'Все':
        photo_dict = vk.get_all_photos(vk_user_id, int(count))
        print(f'Получено {count} фотографий из всех альбомов!')
    else:
        print('Место получения фотографий введено неверно!!!')

    disk = input('Введите платформу на которую будем сохранять фотографии (Yandex или Google): ')
    match disk:
        case 'Yandex':
            extract_yandex(photo_dict, vk_user_id, int(count))
        case 'Google':
            extract_google(photo_dict, vk_user_id, int(count))
        case _:
            print('Платформа не определена!')