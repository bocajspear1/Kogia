import uuid
import os
import stat
import time
import hashlib


from .objects import VertexObject

class Metadata(VertexObject):

    def __init__(self, key=None, id=None):
        super().__init__('metadata', id)
        self._key = key 
        self._value = ""

    @property
    def key(self):
        return self._key 

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def to_dict(self):
        my_uuid  = hashlib.sha256((self._key + ":" + self._value).encode())
        return {
            "key": self._key,
            "value": self._value,
            "uuid": my_uuid.hexdigest()
        }

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('uuid', '')
        self._key = data_obj.get('name', '')
        self._value = data_obj.get('value', '')

    def save(self, db):
        self.save_doc(db, self.to_dict())

    def load(self, db):
        document = {}
        if self.id is None:
            document = self.load_doc(db, field='key', value=self._key)
        else:
            document = self.load_doc(db)

        self.from_dict(document)

class SubmissionFile(VertexObject):

    @classmethod
    def new(cls, parent_dir, filename):
        new_cls = cls(uuid=str(uuid.uuid4()))
        new_cls._modified = True
        new_cls._parent_path = parent_dir
        new_cls._name = filename
        return new_cls
    
    def __init__(self, uuid=None, id=None):
        super().__init__('files', id)

        self._name = ""
        self._uuid = uuid
        self._parent_path = ""
        self._mime_type = ""
        self._unpacked_archive = False
        self._exec_format = "" # e.g. elf or pe
        self._exec_type = "" # library or executable
        self._exec_arch = ""
        self._exec_bits = ""
        self._metadata = []

    def to_dict(self):
        return {
            "uuid": self._uuid,
            "name": self._name,
            "parent_path": self._parent_path,
            "mime_type": self._mime_type,
            "unpacked_archive": self._unpacked_archive,
            "exec_format": self._exec_format,
            "exec_type": self._exec_type,
            "exec_arch": self._exec_arch,
            "exec_bits": self._exec_bits,
        }

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('uuid', '')
        self._name = data_obj.get('name', '')
        self._parent_path = data_obj.get('parent_path', '')
        self._mime_type = data_obj.get('mime_type', '')
        self._unpacked_archive = data_obj.get('unpacked_archive', False)
        self._exec_format = data_obj.get('exec_format', '')
        self._exec_type = data_obj.get('exec_type', '')
        self._exec_arch = data_obj.get('exec_arch', '')
        self._exec_bits = data_obj.get('exec_bits', '')

    @property
    def extension(self):
        _, ext = os.path.splitext(self._name)
        return ext

    @property
    def file_path(self):
        return os.path.join(self._parent_path, self._name)

    @property
    def uuid(self):
        return self._uuid

    @property
    def name(self):
        return self._name

    def set_read_only(self):
        path = self.file_path

        if os.path.exists(path):
            os.chmod(path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
            return True
        else:
            return False

    def save(self, db):
        self.save_doc(db, self.to_dict())
        for data in self._metadata:
            data.save(db)
            self.insert_edge(db, 'has_metadata', data.id)


    def load(self, db):
        document = {}
        if self.id is None:
            document = self.load_doc(db, field='uuid', value=self._uuid)
        else:
            document = self.load_doc(db)

        self.from_dict(document)

        items = self.get_connected_to(db, 'has_metadata')
        for item in items:
            load_data = Metadata(id=item['_to'])
            load_data.load(db)
            self._metadata.append(load_data)

    @property
    def mime_type(self):
        return self._mime_type

    @mime_type.setter
    def mime_type(self, mime_type):
        if "/" not in mime_type:
            raise ValueError("Invalid MIME type (missing /)")
        self._mime_type = mime_type

    @property
    def exec_format(self):
        return self._exec_format

    @exec_format.setter
    def exec_format(self, exec_format):
        self._exec_format = exec_format

    @property
    def exec_type(self):
        return self._exec_type

    @exec_type.setter
    def exec_type(self, exec_type):
        if exec_type not in ('library', 'executable', 'script'):
            raise ValueError("Invalid exec type, should be 'library', 'executable', or 'script'")
        self._exec_type = exec_type

    @property
    def exec_arch(self):
        return self._exec_arch

    @exec_arch.setter
    def exec_arch(self, exec_arch):
        self._exec_arch = exec_arch

    @property
    def exec_bits(self):
        return self._exec_bits

    @exec_bits.setter
    def exec_bits(self, exec_bits):
        if exec_bits not in ('64', '32', '16'):
            raise ValueError("Invalid bit, should string of '64', '32', or '16'")
        self._exec_bits = exec_bits

    def is_unpacked_archive(self):
        self._unpacked_archive = True

    def is_not_unpacked_archive(self):
        self._unpacked_archive = False

    def add_metadata(self, key, value):
        found = False
        for data in self._metadata:
            if data.key == key:
                found = True
                data.value = value 
        
        if not found:
            new_data = Metadata(key=key)
            new_data.value = value
            self._metadata.append(new_data)


class Submission(VertexObject):
    

    @classmethod
    def new(cls, base_dir):
        base_dir = os.path.abspath(base_dir)
        new_cls = cls(uuid=str(uuid.uuid4()))
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        new_cls._modified = True
        new_cls._base_dir = base_dir
        return new_cls

    @property
    def uuid(self):
        return self._uuid

    @property
    def owner(self):
        return self._owner

    def __init__(self, uuid=None, id=None):
        super().__init__('submissions', id)

        if uuid == None and self.id == None:
            raise ValueError("Either id or uuid must be set")

        self._uuid = uuid
        self._submit_time = int(time.time())
        self._owner = ""
        self._base_dir = ""
        self._description = ""

        self._files = []
        self._modified = False

    @property
    def submission_dir(self):
        full_path = os.path.join(self._base_dir, str(self._uuid))
        if not os.path.exists(full_path):
            os.mkdir(full_path)
        return full_path

    def get_file(self, name=None, uuid=None):
        for file in self._files:
            if name is not None and file.name == name:
                return file
            elif uuid is not None and file.uuid == uuid:
                return file

        return None

    def get_files(self):
        return self._files

    def add_file(self, filename):
        
        found = self.get_file(filename)
        if found is None:
            self._modified = True
            new_file = SubmissionFile.new(self.submission_dir, filename)
            self._files.append(new_file)
            return new_file
        else:
            return None

    def load(self, db):
        document = {}
        if self.id is None:
            document = self.load_doc(db, field='uuid', value=self._uuid)
        else:
            document = self.load_doc(db)

        self.from_dict(document)

        items = self.get_connected_to(db, 'has_file')
        for item in items:
            load_file = SubmissionFile(id=item['_to'])
            load_file.load(db)
            self._files.append(load_file)

    def to_dict(self, full=False):
        data_dict = {
            "uuid": self._uuid,
            "owner": self._owner,
            "submit_time": self._submit_time,
            'description': self._description
        }
        if full:
            files_list = []
            for file in self._files:
                files_list.append(file.to_dict())
            data_dict['files'] = files_list
            return data_dict
        else:
            return data_dict

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('uuid', '')
        self._owner = data_obj.get('owner', '')
        self._submit_time = data_obj.get('submit_time', 0)
        

    def save(self, db):
        self.save_doc(db, self.to_dict())

        for file in self._files:
            file.save(db)
            self.insert_edge(db, 'has_file', file.id)
        