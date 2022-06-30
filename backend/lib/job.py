from multiprocessing.sharedctypes import Value
import time
import uuid
import copy

from backend.lib.submission import Submission
from .objects import CollectionObject


class Job(CollectionObject):

    @classmethod
    def new(cls, submission, primary, db):
        new_cls = cls(db, uuid=str(uuid.uuid4()))
        new_cls._submission = submission
        new_cls._primary = primary
        return new_cls


    def __init__(self, db, uuid=None, id=None):
        super().__init__('jobs', id)

        self._user = ""
        self._submission = None
        self._primary = None
        self._start_time = int(time.time())
        self._complete_time = 0
        self._complete = False
        self._error = ""
        self._plugins = []
        self._uuid = uuid
        self._db = db

    @property
    def complete(self):
        return self._complete

    @complete.setter
    def complete(self, new_state):
        if new_state in (True, False):
            self._complete = new_state
            if self._complete == True:
                self._complete_time = int(time.time())
        else:
            raise ValueError("Invalid type for complete")

    @property
    def error(self):
        return self._error

    @property
    def uuid(self):
        return self._uuid

    @property
    def db(self):
        return self._db

    @property
    def primary(self):
        return self._primary

    @property
    def submission(self):
        return self._submission

    def add_plugin_list(self, plugin_list):
        for item in plugin_list:
            self.add_plugin(item)

    def add_plugin(self, new_plugin):
        found = False
        for plugin in self._plugins:
            if plugin.__name__ == new_plugin.__name__:
                found = True
        
        if not found:
            self._plugins.append(new_plugin)
            
    def to_dict(self):
        plugin_list = []
        for plugin in self._plugins:
            plugin_list.append(plugin.__name__)
        return {
            "uuid": self._uuid,
            "user": self._user,
            "primary": self._primary,
            "start_time": self._start_time,
            "complete_time": self._complete_time,
            "complete": self._complete,
            "error": self._error,
            "plugins": plugin_list,
            "submission": self._submission.uuid
        }

    def from_dict(self, pm, data_obj):
        self._uuid = data_obj.get('uuid', '')
        self._name = data_obj.get('name', '')
        self._primary = data_obj.get('primary', '')
        self._start_time = data_obj.get('start_time', 0)
        self._complete_time = data_obj.get('complete_time', 0)
        self._complete = data_obj.get('complete', False)
        self._error = data_obj.get('error', '')

        if 'submission' in data_obj:
            load_sub = Submission(uuid=data_obj['submission'])
            load_sub.load(self._db)
            self._submission = load_sub
        else:
            self._submission = None

        if 'plugins' in data_obj:
            for item in data_obj['plugins']:
                self._plugins.append(pm.get_plugin(item))


    def get_plugin_list(self):
        return copy.deepcopy(self._plugins)

    def save(self):
        self.save_doc(self._db, self.to_dict())
        self._submission.save(self._db)

    def load(self, pm):
        doc = self.load_doc(self._db, 'uuid', self._uuid)
        self.from_dict(pm, doc)


