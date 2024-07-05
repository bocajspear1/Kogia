from multiprocessing.sharedctypes import Value
import uuid
import os
import stat
import time
import hashlib
import shutil

from .objects import VertexObject, VertexObjectWithMetadata, FilestoreObject
from .helpers import safe_uuid

class SubmissionFile(VertexObjectWithMetadata, FilestoreObject):
    """Object for a single file submitted as part of a submission.
    """

    @classmethod
    def new(cls, filestore, store_prefix, filename):
        new_cls = cls(uuid=str(uuid.uuid4()))
        
        # Private in FilestoreObject
        new_cls._modified = True
        new_cls._name = filename
        new_cls._filestore = filestore
        new_cls._file_id = f"{store_prefix}:{filename}-{new_cls.uuid}"
        return new_cls
    
    def __init__(self, uuid=None, id=None, filestore=None):
        VertexObjectWithMetadata.__init__(self, 'files', 'has_metadata', id)
        FilestoreObject.__init__(self, filestore, "", "")
        # super().__init__('files', 'has_metadata', id)

        self._uuid = safe_uuid(uuid)
        
        self._mime_type = ""
        self._unpacked_archive = False
        self._exec_format = "" # e.g. elf or pe
        self._exec_type = "" # library or executable
        self._exec_arch = ""
        self._exec_bits = ""
        self._exec_interpreter = ""
        self._exec_packer = ""
        self._target_os = ""
        self._hash = ""
        self._parent = ""
        self._dropped = False

        self._handle = None

    # def __del__(self):
    #     self.close_file()

    def to_dict(self):
        return {
            "_key": self._uuid,
            "uuid": self._uuid,
            "name": self._name,
            "file_id": self._file_id,
            "dropped": self._dropped,
            "mime_type": self._mime_type,
            "unpacked_archive": self._unpacked_archive,
            "exec_format": self._exec_format,
            "exec_type": self._exec_type,
            "exec_arch": self._exec_arch,
            "exec_bits": self._exec_bits,
            "exec_interpreter": self._exec_interpreter,
            "exec_packer": self._exec_packer,
            "target_os": self._target_os,
            "hash": self._hash
        }

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('_key', '')
        self._name = data_obj.get('name', '')
        self._file_id = data_obj.get('file_id', '')
        self._mime_type = data_obj.get('mime_type', '')
        self._unpacked_archive = data_obj.get('unpacked_archive', False)
        self._exec_format = data_obj.get('exec_format', '')
        self._exec_type = data_obj.get('exec_type', '')
        self._exec_arch = data_obj.get('exec_arch', '')
        self._exec_bits = data_obj.get('exec_bits', '')
        self._exec_interpreter = data_obj.get('exec_interpreter', '')
        self._target_os = data_obj.get('target_os', '')
        self._hash = data_obj.get('hash', '')

    @property
    def uuid(self):
        return self._uuid

    def set_parent(self, parent_file):
        self._parent = parent_file.id

    def save(self, db):
        self.save_doc(db, self.to_dict())
        self.reset_modified()

        self.save_metadata(db)

        if self._parent != "":
            self.insert_edge(db, 'has_parent', self._parent)


    def load(self, db):
        document = {}
        if self.id is None:
            document = self.load_doc(db, field='_key', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is not None:
            self.from_dict(document)
            self.reset_modified()
        else:
            self._uuid = None

    @property
    def dropped(self):
        return self._dropped

    @dropped.setter
    def dropped(self, new_dropped):
        self._dropped = new_dropped

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
    def exec_bits(self, new_exec_bits):
        if new_exec_bits not in ('64', '32', '16', 'any'):
            raise ValueError("Invalid bit, should string of '64', '32', '16' or 'any'")
        self._exec_bits = new_exec_bits

    @property
    def exec_interpreter(self):
        return self._exec_interpreter

    @exec_interpreter.setter
    def exec_interpreter(self, new_exec_interpreter):
        self._exec_interpreter = new_exec_interpreter

    @property
    def exec_packer(self):
        return self._exec_packer

    @exec_packer.setter
    def exec_packer(self, new_exec_packer):
        self._exec_packer = new_exec_packer

    @property
    def target_os(self):
        return self._target_os

    @target_os.setter
    def target_os(self, new_target_os):
        self._target_os = new_target_os

    def is_unpacked_archive(self):
        self._unpacked_archive = True

    def is_not_unpacked_archive(self):
        self._unpacked_archive = False

class Submission(VertexObject):
    """Object for a submission, a group of files that a Job operates on.
    """

    COLLECTION_NAME = 'submissions'

    @classmethod
    def new(cls, filestore, owner):
        new_cls = cls(uuid=str(uuid.uuid4()))
        new_cls._modified = True
        new_cls._filestore = filestore
        new_cls._owner = owner
        return new_cls

    @classmethod
    def list_dict(cls, db, file_uuid=None):
        if file_uuid is None:
            submission_list = db.get_vertex_list_sorted(cls.GRAPH_NAME, cls.COLLECTION_NAME, "submit_time", "DESC")
        else:
            filter_file = SubmissionFile(uuid=file_uuid)
            filter_file.load(db)
            submission_list = db.get_connected_to(cls.GRAPH_NAME, filter_file.id, cls.COLLECTION_NAME, filter_edges=['has_file'], sort_by=(cls.COLLECTION_NAME, 'submit_time', 'DESC'))
        for submission_item in submission_list:
            del submission_item['_rev']
            del submission_item['_id']
            submission_item['uuid'] = submission_item['_key']
        return submission_list
        
    @property
    def uuid(self):
        return self._uuid

    @property
    def owner(self):
        return self._owner

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def __init__(self, uuid=None, id=None):
        super().__init__(self.COLLECTION_NAME, id)

        if uuid == None and self.id == None:
            raise ValueError("Either id or uuid must be set")

        self._uuid = safe_uuid(uuid)
        self._submit_time = int(time.time())
        self._owner = ""
        self._filestore = None
        self._submission_dir = ""
        self._description = ""
        self._name = ""

        self._files = []
        self._modified = False
        self._files_loaded = False

    @property
    def submission_dir(self):
        """Temporary directory where the files of the submission are stored. 

        This directory is mounted to Docker containers during plugin operation.
        """
        if self._submission_dir == "":
            self._submission_dir = os.path.join("/tmp", "kogia-" + str(self._uuid))
            if not os.path.exists(self._submission_dir):
                os.mkdir(self._submission_dir)
        for file in self._files:
            # # Ignore dropped files
            # if file.dropped:
            #     continue
            file_path = os.path.join(self._submission_dir, file.name)
            if not os.path.exists(file_path):
                self._filestore.copy_file_to(file.file_id, file_path)
        return self._submission_dir

    def get_file(self, name=None, uuid=None):
        if not self._files_loaded:
            raise ValueError("File not loaded, call load_files first")
        for file in self._files:
            if name is not None and file.name == name:
                return file
            elif uuid is not None and file.uuid == uuid:
                return file

        return None

    @property
    def files(self):
        if not self._files_loaded:
            raise ValueError("File not loaded, call load_files first")
        return self._files

    def generate_file(self, filename):
        """Creates and initializes a SubmissionFile object.
        """
        found = self.get_file(filename)
        if found is None:
            self._modified = True
            new_file = SubmissionFile.new(self._filestore, self._uuid, filename)
            return new_file
        else:
            return found

    def add_file(self, new_file, dropped=False):
        """Inserts a SubmissionFile object into the Submission's file list.

        Use 'generate_file' to initialize a new SubmissionFile easily.
        """
        new_file.update_hash()
        for file in self._files:
            if new_file.hash == file.hash:
                return file
        new_file.dropped = dropped
        self._files.append(new_file)
        

    def load(self, db):
        document = {}
        if self.id is None:
            document = self.load_doc(db, field='_key', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is None:
            self._uuid = None
            return

        self.from_dict(document)
        

    def load_files(self, db, filestore):
        self._files = []
        items = self.get_connected_to(db, 'files', add_edges=True, max=1)
        
        self._filestore = filestore

        for item in items:
            dropped = False
            if '_edge' in item and 'dropped' in item['_edge']:
                dropped = item['_edge']['dropped']
            load_file = SubmissionFile(id=item['_id'], filestore=filestore)
            load_file.from_dict(item)
            load_file.dropped = dropped
            self._files.append(load_file)
        self._files_loaded = True
        

    def to_dict(self, files=False):
        data_dict = {
            "_key": self._uuid,
            "uuid": self._uuid,
            "owner": self._owner,
            "submit_time": self._submit_time,
            "name": self._name,
            "description": self._description,
        }
        if files:
            files_list = []
            for file in self._files:
                files_list.append(file.to_dict())
            data_dict['files'] = files_list
            return data_dict
        else:
            return data_dict

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('_key', '')
        self._owner = data_obj.get('owner', '')
        self._submit_time = data_obj.get('submit_time', 0)
        self._name = data_obj.get('name', '')
        self._description = data_obj.get('description', '')
        

    def save(self, db):
        self.save_doc(db, self.to_dict())

        for file in self._files:
            file.save(db)
            self.insert_edge(db, 'has_file', file.id, {
                "dropped": file.dropped
            })
        