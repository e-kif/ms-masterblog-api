import json
import os
import datetime


class Storage:

    def __init__(self, filename='posts.json'):
        self._storage_filename = filename
        if not os.path.exists(self._storage_filename):
            self.initiate_empty_json()
        try:
            with open(self._storage_filename, 'r', encoding='utf8') as handle:
                self._storage = json.loads(handle.read())
        except json.decoder.JSONDecodeError:
            print(f'Storage file {self._storage_filename} has invalid JSON structure or syntax')
            backup = f'{self._storage_filename}_{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.bak'
            os.rename(self._storage_filename, backup)
            print(f'Invalid storage file was renamed to {backup}. Proceeding with empty file {self._storage_filename}')
            self.initiate_empty_json()
            self._storage = list()

    def initiate_empty_json(self):
        with open(self._storage_filename, 'w', encoding='utf8') as handle:
            handle.write(json.dumps([]))

    @property
    def posts(self):
        return self._storage

    @posts.setter
    def posts(self, posts_data):
        self._storage = posts_data
        self.update_storage_file(posts_data)

    def update_storage_file(self, posts_data):
        with open(self._storage_filename, 'w', encoding='utf8') as handle:
            handle.write(json.dumps(posts_data))

    def append(self, item):
        if isinstance(self._storage, list):
            self._storage.append(item)
            self.update_storage_file(self._storage)
        else:
            print('Wrong storage file structure. New post was not added.'
                  'Check that the root structure of the storage json file is a list')

    def remove(self, item):
        if isinstance(self._storage, list):
            self._storage.remove(item)
            self.update_storage_file(self._storage)
        else:
            print('Wrong storage file structure. New post was not added.'
                  'Check that the root structure of the storage json file is a list')
