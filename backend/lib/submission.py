import uuid
import os
import stat
import time


class VertexObject():

    def __init__(self, collection, id=None):
        self._graph_name = 'kogia-graph'
        self._modified = False 
        # self._db = db
        self._collection = collection
        self._id = id

    @property
    def id (self):
        return self._id

    def set_modified(self):
        self._modified = True 

    def reset_modified(self):
        self._modified = False

    def to_json(self):
        raise NotImplementedError

    def save_doc(self, db, data):
        if self._id is None:
            self._id = db.insert_vertex(self._graph_name, self._collection, data)
        else:
            db.update_vertex(self._graph_name, self._collection, self._id, data)

    def load_doc(self, db, field=None, value=None):
        if field is not None:
            return db.get_vertex_by_match(self._graph_name, self._collection, field, value)
        else:
            if self._id is not None:
                return db.get_by_id(self._graph_name, self._collection, self._id)
            else:
                return None

    def insert_edge(self, db, collection, to_item, data=None):
        db.insert_edge(self._graph_name, collection, self._id, to_item, data=data)

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
        return {
            "key": self._key,
            "value": self._value
        }

    def save(self, db):
        self.save_doc(db, self.to_dict())

    def load(self, db):
        pass

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
        print(new_cls.submission_dir)
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

        self._files = []
        self._modified = False

    @property
    def submission_dir(self):
        full_path = os.path.join(self._base_dir, str(self._uuid))
        if not os.path.exists(full_path):
            os.mkdir(full_path)
        return full_path

    def _get_file(self, name=None, uuid=None):
        for file in self._files:
            if name is not None and file.name == name:
                return file
            elif uuid is not None and file.uuid == uuid:
                return file

        return None

    def add_file(self, filename):
        
        found = self._get_file(filename)
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

        print(document)

    def save(self, db):
        self.save_doc(db, {
            "uuid": self._uuid,
            "owner": self._owner,
            "submit_time": self._submit_time
        })

        for file in self._files:
            file.save(db)
            self.insert_edge(db, 'has_file', file.id)
        