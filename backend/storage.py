import json
import os


class Storage:

    def __init__(self, filename='posts.json'):
        self._storage_filename = filename
        if not os.path.exists(self._storage_filename):
            with open(self._storage_filename, 'w', encoding='utf8') as handle:
                handle.write('[]')
        with open(self._storage_filename, 'r', encoding='utf8') as handle:
            self._storage = json.loads(handle.read())

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
