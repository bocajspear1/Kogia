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
    def new(cls, proc_name, pid, is_primary=False, file=None):
        new_cls = cls(uuid=str(uuid.uuid4()))
        new_cls._name = proc_name
        new_cls._pid = pid
        new_cls._is_primary = is_primary
        new_cls._file = file
        return new_cls


    def __init__(self, id=None, uuid=None):
        super().__init__(self.COLLECTION_NAME, id)
        self._uuid = uuid
        self._pid = None
        self._file = None
        self._name = ""
        self._start_time = 0
        self._end_time = 0
        self._is_primary = False

    @property
    def is_primary(self):
        return self._is_primary

    @property
    def file_uuid(self):
        if self._file is not None:
            return self._file.uuid
        else:
            return None

    @property
    def pid(self):
        return self._pid

    # @pid.setter
    # def pid(self, new_pid):
    #     self._pid = new_pid
    #     # self._gen_uuid()
        

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