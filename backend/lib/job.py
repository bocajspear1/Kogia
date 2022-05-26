import time
import uuid
from .objects import CollectionObject


class Job(CollectionObject):

    @classmethod
    def new(cls, submission, primary, db):
        new_cls = cls(uuid=str(uuid.uuid4()))
        new_cls._submission = submission
        new_cls._primary = primary
        new_cls._db = db
        return new_cls


    def __init__(self, db=None, uuid=None, id=None):
        super().__init__('jobs', id)

        self._user = ""
        self._submission = None
        self._primary = None
        self._start_time = int(time.time())
        self._complete = False
        self._plugins = []
        self._db = db

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
            if plugin.__class__.__name__ == new_plugin.__class__.__name__:
                found = True
        
        if not found:
            self._plugins.append(new_plugin)

    def get_plugin_list(self):
        return self._plugins

    def save(self):
        self._submission.save(self._db)

