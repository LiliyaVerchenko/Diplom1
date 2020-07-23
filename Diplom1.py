from pprint import pprint
import os
import json
import requests
import time

class Backup_copying():
    def __init__(self, token: str, user_id: str):
        self.token = token
        self.headers_YD = {'Accept': 'application/json', 'Authorization': self.token}
        self.user_id = user_id

    def download_photosVK(self): # сохранение фото в локальную папку
        # получаем фото со стены
        params_wall = {'access_token': '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008',
                       'owner_id': self.user_id, 'photo_sizes': '1', 'album_id': 'wall', 'extended': '1', 'count': '5', 'v': 5.21}
        get_photos_wall = requests.get('https://api.vk.com/method/photos.get', params=params_wall).json()['response']['items']
        # получаем фото профиля
        params_profile = {'access_token': '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008',
                          'owner_id': self.user_id, 'photo_sizes': '1', 'album_id': 'profile', 'extended': '1', 'count': '5', 'v': 5.21}
        get_photos_profile = requests.get('https://api.vk.com/method/photos.get', params=params_profile).json()['response']['items']
        # получаем общий список фото
        get_photos = get_photos_wall + get_photos_profile
        file_photo1 = []  # создаем список с выгрузкой в него необходимых параметров
        for photo in get_photos:
            file_photo1.append({'likes': photo['likes']['count'], 'date_upload': photo['date'],
                                'link': photo['sizes'][-1]['src'], 'size': photo['sizes'][-1]['type']})
        file_photo = sorted(file_photo1, key=lambda x: x['likes'])
        end_list = {}  # создаем словарь с названием фото и ссылкой
        end_list1 = []  # создаем список с названием фото и размером
        for photo in file_photo:
            likes = photo['likes']
            size = photo['size']
            if f'{likes}.jpg' not in list(end_list.keys()):
                file_name = f'{likes}.jpg'
                end_list[file_name] = photo['link']
            else:
                rename = str(likes) + str(photo['date_upload'])
                file_name = f'{rename}.jpg'
                end_list[file_name] = photo['link']
            end_list1.append({'file_name': file_name, 'size': size})
        with open ('Photo_vk.json', 'w', encoding='utf8') as file:  # запись данных о фото end_list1 в файл
            k = file.write(json.dumps(end_list1))
        for photo, link in end_list.items():            # загрузка фото в локальную папку Photo
            image = requests.get(link)
            full_file_name = os.path.join('Photo', photo)
            with open(full_file_name, 'wb') as file:
                file.write(image.content)
        print('Изображения успешно сохранены в локальную папку Photo')
        return print()

    def upload_photos(self, path):    # загружаем фото на яндекс диск
        self.path = path
        file_list = os.listdir(self.path)    # получаем список файлов в директории
        path_list = []                        # получаем список путей к каждому файлу
        for file in file_list:
            path = os.path.join(self.path, file)
            path_list.append(path)
        create_folder = requests.put('https://cloud-api.yandex.net:443/v1/disk/resources?path=%2FPhoto_VK',   # создаем папку на Диске
                                     headers=self.headers_YD)
        for i, path1 in enumerate(path_list, 1):     # открываем и читаем каждый файл
            with open(path1, 'rb') as f:
                _file = f.read()
                                                     # получаем ссылку для загрузки на диск и статус загрузки
            response = requests.get(f'https://cloud-api.yandex.net:443/v1/disk/resources/upload?path=/Photo_VK/{os.path.basename(path1)}',
                                       headers=self.headers_YD).json()
            link_upload = response['href']
            operation_id = response['operation_id']
            upload = requests.put(link_upload, headers=self.headers_YD, data=_file)  # загружаем файл на диск по ссылке
            while True:   # прогресс бар
                status = requests.get(f'https://cloud-api.yandex.net/v1/disk/operations/{operation_id}', headers=self.headers_YD).json()['status']
                if status == 'success':
                    break
                time.sleep(1)
            print(f'Изображение "{os.path.basename(path1)}" {str(i)}/{str(len(path_list))} успешно загружено на диск')
        print()
        return print('Загрузка завершена')

if __name__ == '__main__':
    token1 = input('Введите токен с Полигона Яндекс.Диска ')
    token = 'OAuth ' + token1
    user_id = input('Введите идентификатор пользователя VK ')
    my_file_path = r'Photo'
    uploader = Backup_copying(token, user_id)  # создаем экземпляр класса
    uploader.download_photosVK()
    uploader.upload_photos(my_file_path)

