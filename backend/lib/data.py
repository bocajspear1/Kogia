import uuid
import os
import stat
import time
import hashlib
from enum import Enum

from .submission import SubmissionFile


from .db import DBNotUniqueError
from .objects import VertexObject

class SIGNATURE_SEVERITY:
    INFO = 1 # Just informational
    CAUTION = 2 # Sometimes used for malicious activity
    SUSPICIOUS = 3 # Often used for malicious activies
    MALICIOUS = 4 # Known to be malicious

class SignatureMatch(VertexObject):

    COLLECTION_NAME = 'signature_matches'

    @classmethod
    def new(cls, signature, file):
        new_cls = cls(uuid=str(uuid.uuid4()))
        new_cls._signature = signature
        new_cls._file = file
        return new_cls

    def __init__(self, uuid=None, id=None):
        super().__init__(self.COLLECTION_NAME, id)
        self._uuid = uuid
        self._file = None
        self._signature = None
        self._match_time = int(time.time()) 


    @property
    def file_uuid(self):
        return self._file.uuid

    def to_dict(self):
        if self._uuid == "":
            self._gen_uuid()
        return {
            "uuid": self._uuid,
            "match_time": self._match_time,
        }

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('uuid', '')
        self._match_time = data_obj.get('match_time', '')
        if 'signature' in data_obj:
            self._signature = Signature(uuid=data_obj['signature'])


    def save(self, db):
        try:
            self.save_doc(db, self.to_dict())
        except DBNotUniqueError:
            pass

        if self._file is not None:
            if self._file.id is None:
                self._file.save(db)
            self._file.insert_edge(db, 'has_match', self.id)

        if self._signature is not None:
            if self._signature.id is None:
                self._signature.save(db)
            self.insert_edge(db, 'matched_signature', self._signature.id)
        

    def load(self, db):
        document = {}
        if self.id is None:
            if self._uuid == "":
                self._gen_uuid()
            document = self.load_doc(db, field='uuid', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is not None:
            self.from_dict(document)

    def load_file(self, db):
        my_file_list = self.get_connected_to(db, 'has_match')
        if len(my_file_list) > 0:
            self._file = SubmissionFile(id=my_file_list[0]['_id'])
            self._file.from_dict(my_file_list[0])
    

    def load_signature(self, db):
        my_sig_list = self.get_connected_to(db, 'matched_signature')
        if len(my_sig_list) > 0:
            self.my_sig_list = Signature(id=my_sig_list[0]['_id'])
            self._signature.from_dict(my_sig_list[0])

class Signature(VertexObject):

    COLLECTION_NAME = 'signatures'

    def __init__(self, uuid=None, id=None):
        super().__init__(self.COLLECTION_NAME, id)
        self._uuid = uuid
        self._name = ""
        self._description = ""
        self._plugin_name = ""
        self._severity = SIGNATURE_SEVERITY.INFO

    @property
    def uuid(self):
        return self._uuid

    #
    # Read/Write properties
    #

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self.set_modified()
        self._name = new_name
    
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, new_description):
        self.set_modified()
        self._description = new_description

    @property
    def plugin_name(self):
        return self._plugin_name

    @plugin_name.setter
    def plugin_name(self, new_plugin_name):
        self.set_modified()
        self._plugin_name = new_plugin_name

    @property
    def severity(self):
        return self._severity

    @severity.setter
    def severity(self, new_severity):
        # if not isinstance(new_severity, SIGNATURE_SEVERITY):
        #     raise ValueError("Invalid severity")
        self.set_modified()
        self._severity = new_severity

    # Generate the UUID from the plugin_name and signature name
    def _gen_uuid(self):
        my_uuid = hashlib.sha256((self.plugin_name + ":" + self.name + ":" + str(self.severity)).encode())
        self._uuid = my_uuid.hexdigest()
        self.set_modified()

    def to_dict(self):
        if self._uuid == "" or self._uuid is None:
            self._gen_uuid()
        return {
            "uuid": self._uuid,
            "name": self.name,
            "description": self.description,
            "plugin": self.plugin_name,
            "severity": str(self.severity)
        }

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('uuid', '')
        self.name = data_obj.get('name', '')
        self.description = data_obj.get('description', '')
        self.plugin_name = data_obj.get('plugin', '')
        self.severity = SIGNATURE_SEVERITY[data_obj.get('severity', 'INFO')]

    def save(self, db):
        if self.is_modified:
            try:
                self.save_doc(db, self.to_dict())
                self.reset_modified()
            except DBNotUniqueError:
                pass

    def load(self, db):
        document = {}
        if self.id is None:
            if self._uuid == "":
                self._gen_uuid()
            document = self.load_doc(db, field='uuid', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is not None:
            self.from_dict(document)
            self.reset_modified()

class Report(VertexObject):

    def __init__(self, id=None, uuid=None):
        super().__init__('reports', id)
        self._uuid = uuid
        self._value = ""
        self._file_uuid = ""
        self.name = ""

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._gen_uuid()

    @property
    def file_uuid(self):
        return self._file_uuid

    @file_uuid.setter
    def file_uuid(self, file_uuid):
        self._file_uuid = file_uuid

    @property
    def uuid(self):
        return self._uuid
    
    def _gen_uuid(self):
        my_uuid  = hashlib.sha256((self._value).encode())
        self._uuid = my_uuid.hexdigest()

    def to_dict(self):
        if self._uuid == "":
            self._gen_uuid()
        return {
            "uuid": self._uuid,
            "value": self._value,
            "file_uuid": self._file_uuid,
            "name": self.name
        }

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('uuid', '')
        self._value = data_obj.get('value', '')
        self._file_uuid = data_obj.get('file_uuid', '')
        self.name = data_obj.get('name', '')

    def save(self, db):
        try:
            self.save_doc(db, self.to_dict())
        except DBNotUniqueError:
            pass

    def load(self, db):
        document = {}
        if self.id is None:
            if self._uuid == "":
                self._gen_uuid()
            document = self.load_doc(db, field='uuid', value=self._uuid)
        else:
            document = self.load_doc(db)

        self.from_dict(document)

class ExecInstance(VertexObject):

    COLLECTION_NAME = 'exec_instance'

    @classmethod
    def new(cls, module_name, run_os):
        new_cls = cls(uuid=str(uuid.uuid4()))
        new_cls.exec_module = module_name
        new_cls._run_os = run_os
        return new_cls

    def __init__(self, id=None, uuid=None):
        super().__init__(self.COLLECTION_NAME, id)
        self._uuid = uuid
        self._start_time = 0
        self._end_time = 0
        self.exec_module = ""
        self._run_os = ""
        self._processes = []
        self._syscall_counter = 0
        self._event_counter = 0

    def to_dict(self, full=True):
        ret_dict = {
            "uuid": self._uuid,
            "start_time": self._start_time,
            "end_time": self._end_time,
            "exec_module": self.exec_module,
            "run_os": self._run_os,
        }
        if full:
            ret_dict["processes"] = []
            for proc in self._processes:
                ret_dict["processes"].append(proc.to_dict(get_children=True))
        return ret_dict

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('uuid', '')
        self._start_time = data_obj.get('start_time', 0)
        self._end_time = data_obj.get('end_time', 0)
        self.exec_module = data_obj.get('exec_module', '')
        self._run_os = data_obj.get('run_os', '')
        if 'signature' in data_obj:
            self._signature = Signature(uuid=data_obj['signature'])


    def save(self, db):
        try:
            self.save_doc(db, self.to_dict(full=False))
        except DBNotUniqueError:
            pass

        if self._processes is not None:
            for process in self._processes:
                process.save(db)
                self.insert_edge(db, 'has_process', process.id)

    def load(self, db):
        document = {}
        if self.id is None:
            document = self.load_doc(db, field='uuid', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is not None:
            self.from_dict(document)

    def load_processes(self, db):
        items = self.get_connected_to(db, 'processes', filter_edges=['has_process'])
        for item in items:
            load_data = Process(id=item['_id'])
            load_data.from_dict(item)
            load_data.load_child_processes(db)
            self._processes.append(load_data)

    def add_process(self, proc_path, pid):
        new_proc = Process.new(proc_path, pid)
            
        self._processes.append(new_proc)
        return new_proc
    
    @property
    def uuid(self):
        return self._uuid

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, new_time):
        self._start_time = new_time

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, new_time):
        self._end_time = new_time

class Event(VertexObject):
    def __init__(self, id=None, uuid=None):
        super().__init__('events', id)
        self._uuid = uuid
        self._pid = None
        self._tid = None
        self._name = ""
        self._event_time = 0


class Process(VertexObject):

    COLLECTION_NAME = 'processes'

    @classmethod
    def new(cls, proc_path, pid):
        new_cls = cls(uuid=str(uuid.uuid4()))
        new_cls._path = proc_path
        new_cls._pid = pid
        return new_cls


    def __init__(self, id=None, uuid=None):
        super().__init__(self.COLLECTION_NAME, id)
        self._uuid = uuid
        self._pid = 0
        self._path = ""
        self._start_time = 0
        self._end_time = 0
        self._syscalls = []
        self._events = []
        self._child_processes = []

    @property
    def pid(self):
        return self._pid
    
    @property
    def path(self):
        return self._path
    
    def to_dict(self, get_children=True):
        ret_dict = {
            "uuid": self._uuid,
            "pid": self._pid,
            "path": self._path,
            "start_time": self._start_time,
            "end_time": self._end_time,
        }
        if get_children:
            ret_dict["child_processes"] = []
            for child_proc in self._child_processes:
                ret_dict["child_processes"].append(child_proc.to_dict(get_children=True))
        return ret_dict

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('uuid', '')
        self._pid = data_obj.get('pid', 0)
        self._path = data_obj.get('path', '')
        self._start_time = data_obj.get('start_time', 0)
        self._end_time = data_obj.get('end_time', 0)

        if 'child_processes' in data_obj:
            for item in data_obj['child_processes']:
                add_proc = Process(uuid=item['uuid'])
                add_proc.from_dict(item)
                self._child_processes.append(add_proc)

    def save(self, db):
        try:
            self.save_doc(db, self.to_dict(get_children=False))
        except DBNotUniqueError:
            pass

        if self._child_processes is not None:
            for process in self._child_processes:
                process.save(db)
                self.insert_edge(db, 'is_child_of', process.id)

    def load(self, db):
        document = {}
        if self.id is None:
            document = self.load_doc(db, field='uuid', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is not None:
            self.from_dict(document)

    def load_child_processes(self, db, get_children=True):
        items = self.get_connected_to(db, 'processes', filter_edges=['is_child_of'], direction='out', max=1)
        for item in items:
            load_data = Process(id=item['_id'])
            load_data.from_dict(item)
            if get_children:
                load_data.load_child_processes(db, get_children=get_children)
            self._child_processes.append(load_data)
    
    def add_child_process(self, proc_path, pid):
        child_proc = Process.new(proc_path, pid)
        self._child_processes.append(child_proc)
        return child_proc

                
