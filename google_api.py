import requests
import json
import io
import time

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from tqdm import tqdm


class GDrive:

    def __init__(self):
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(gauth)
        self.access_token = gauth.attr['credentials'].access_token

    def _create_folder(self, folder_name, root_folder_id = 'root'):

        file_metadata = {
            'title': folder_name,
            'parents': [root_folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }

        try:
            folder = self.drive.CreateFile(file_metadata)
            folder.Upload()
            return f'Folder "{folder_name}" was created successfully'
        except Exception as _ex:
            return 'Не удалось создать папку'

    def _check_folder_exists(self, item_name, folder_id = 'root'):

        lst =self.drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
        for item in lst:
            if item['title'] == str(item_name):
                return item['id']
            else:
                continue

    def create_file(self, photos, user_id, count):

        folder_id = self._check_folder_exists(user_id)
        if folder_id is None:
            self._create_folder(user_id)
            print(f'Folder "{user_id}" was created successfully')
            folder_id = self._check_folder_exists(user_id)

        progress_bar = tqdm(total=count, desc="Processing files", unit="files", ncols=120, colour='#37B6BD')

        for f_name, f_url in photos.items():
            time.sleep(0.2)
            progress_bar.update(1)
            progress_bar.set_postfix(file=f_name)
            file_id = self._check_folder_exists(f_name, str(folder_id))
            if file_id is None:
                metadata = {"name": f_name, "parents": [folder_id]}
                file = {"data": ('metadata', json.dumps(metadata), "application/json"), "file": io.BytesIO(requests.get(f_url).content)}
                requests.post("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true", headers={"Authorization": "Bearer " + self.access_token}, files=file)
                print(f'  File {f_name} created.')
            else:
                print(f'  File {f_name} already exists.')