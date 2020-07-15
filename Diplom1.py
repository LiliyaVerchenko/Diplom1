from pprint import pprint
import os
import json
import requests
import time
from tqdm import tqdm

class Backup_copying():
    def __init__(self, token: str, user_id: str):
        self.token = token
        self.headers_YD = {'Accept': 'application/json', 'Authorization': self.token}
        self.user_id = user_id

    def download_photosVK(self):
        # получить фотки из профиля photos.get
        get_photos = requests.get('https://api.vk.com/method/photos.get', params={'access_token': '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008',
                                                                                  'owner_id': self.user_id, 'photo_sizes': '1', 'album_id': 'profile', 'extended': '1', 'v': 5.21}).json()['response']['items']
        file_photo = []
        for photo in get_photos:
            file_photo.append({'likes': photo['likes']['count'], 'date_upload': photo['date'], 'link': photo['sizes'][-1]['src'], 'size': photo['sizes'][-1]['type']})

        # получаем словарь с названием файла и ссылкой
        end_list = {}
        end_list1 = []
        for photo in file_photo:
            p = photo['likes']
            l = photo['size']
            if f'{p}.jpg' not in list(end_list.keys()):
                file_name = f'{p}.jpg'
                end_list[file_name] = photo['link']
            else:
                rename = str(p) + str(photo['date_upload'])
                file_name = f'{rename}.jpg'
                end_list[file_name] = photo['link']
            end_list1.append({'file_name': file_name, 'size': l})
        # запись данных в файл
        with open ('Photo_vk.json', 'w', encoding='utf8') as file:
            k = file.write(json.dumps(end_list1))
        # загрузка фото на комп
        for photo, link in end_list.items():
            image = requests.get(link)
            full_file_name = os.path.join('Photo', photo)
            with open(full_file_name, 'wb') as file:
                file.write(image.content)
        return print('Файлы сохранены в папку Photo')

    def upload_photos(self, path):
        self.path = path

        file_list = os.listdir(self.path)       # получаем список файлов в директории

        path_list = []             # получаем список путей к каждому файлу
        for file in file_list:
            path = os.path.join(self.path, file)
            path_list.append(path)
        create_folder = requests.put('https://cloud-api.yandex.net:443/v1/disk/resources?path=%2FPhoto_VK',     # создаем папку на Диске
                                     headers=self.headers_YD)
        for path1 in path_list:                 # загружаем фото на диск
            with open(path1, 'rb') as f:           # открываем и читаем каждый файл
                _file = f.read()
            link_upload = requests.get(f'https://cloud-api.yandex.net:443/v1/disk/resources/upload?path=/Photo_VK/{os.path.basename(path1)}',   # получаем ссылку для загрузки на диск
                                       headers=self.headers_YD).json()['href']
            upload = requests.put(link_upload, data=_file)        # загружаем файл на диск по ссылке
        for i in tqdm(link_upload):
            time.sleep(0.01)
        print(f'Файлы успешно загружены на диск')

if __name__ == '__main__':
    token1 = input('Введите токен с Полигона Яндекс.Диска')
    token = 'OAuth ' + token1
    user_id = input('Введите идентификатор пользователя VK ')
    my_file_path = r'C:\Users\Константин\PycharmProjects\Diplom1\Photo'

    uploader = Backup_copying(token, user_id)  # создаем экземпляр класса
    uploader.download_photosVK()
    uploader.upload_photos(my_file_path)

