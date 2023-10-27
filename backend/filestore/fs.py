import os
import stat
import shutil


class FSFileStore():

    def __init__(self, config):
        self._config = config
        self._dir = config['dir']
        if not os.path.exists(self._dir):
            os.mkdir(self._dir)

    def _get_full_path(self, file_id : str):
        print(f"'{file_id}'")
        dir_split = file_id.split(":")
        
        loc = 0
        parent_dir = self._dir
        while loc != len(dir_split)-1:
            subdir = os.path.join(parent_dir, dir_split[0])
            if not os.path.exists(subdir):
                os.mkdir(subdir)
            parent_dir = subdir
            loc += 1

        return os.path.join(parent_dir, dir_split[-1])

    def create_file(self, file_id):
        full_path = self._get_full_path(file_id)
        return open(full_path, "wb")

    def open_file(self, file_id):
        full_path = self._get_full_path(file_id)
        return open(full_path, "rb")
    
    def close_file(self, file_id, file_handle):
        file_handle.close()
        full_path = self._get_full_path(file_id)

        if os.path.exists(full_path):
            os.chmod(full_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    
    def copy_file_to(self, file_id, dest_file):
        full_path = self._get_full_path(file_id)
        shutil.copy(full_path, dest_file)
