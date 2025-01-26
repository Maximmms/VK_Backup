import requests
import time

from tqdm import tqdm

class YANDEXApi:


    YA_API_BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, token):
        self.token = token

    def _get_common_params(self):
        return {
            'Authorization': f'OAuth {self.token}',
        }

    def _get_files(self, user_id):
        name_lst = []
        headers = self._get_common_params()
        params = {'path': user_id, 'limit': 100}
        url = f"{self.YA_API_BASE_URL}"
        try:
            files = requests.get(url, headers=headers, params=params).json()['_embedded']['items']
            for item in files:
                name_lst.append(item['name'])
        except Exception:
            pass
        return name_lst

    def create_file(self, photos, user_id, count: int):
        files = self._get_files(user_id)
        headers = self._get_common_params()
        url = f"{self.YA_API_BASE_URL}/upload"
        folder_params = {'path': user_id}
        requests.put(self.YA_API_BASE_URL, headers=headers, params=folder_params)

        progress_bar = tqdm(total=count, desc="Processing files", unit="files", ncols=120, colour='#37B6BD')
        for f_name, f_url in photos.items():
            time.sleep(0.2)
            progress_bar.update(1)
            progress_bar.set_postfix(file=f_name)
            if f_name not in files:
                file_params = {'path': f'{user_id}/{f_name}', 'url': f_url}
                file = requests.post(url, headers=headers, params=file_params)
                if file.status_code == 202:
                    print(f'  File {user_id}/{f_name} created.')
                else:
                    print(file.status_code)
            else:
                print(f'  File {f_name} already exists.')