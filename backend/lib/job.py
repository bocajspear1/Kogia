from multiprocessing.sharedctypes import Value
import time
import uuid
import copy

from backend.lib.submission import Metadata, Submission, SubmissionFile
from backend.lib.objects import VertexObject
from backend.lib.data import Process, Signature, SignatureMatch, Report


class Job(VertexObject):

    COLLECTION_NAME = 'jobs'

    @classmethod
    def new(cls, submission, primary, db):
        new_cls = cls(db, uuid=str(uuid.uuid4()))
        new_cls._submission = submission
        new_cls._primary = primary
        # Ensure files and their metadata are all loaded
        new_cls._submission.load_files(db)
        for file in new_cls._submission.files:
            file.load_metadata(db)

        return new_cls

    @classmethod
    def list_dict(cls, db, submission_uuid=None):
        new_list = []
        job_items = []
        if submission_uuid is None:
            job_items = db.get_vertex_list_joined(cls.COLLECTION_NAME, {"submissions": ("uuid", "submission")}, sort_by=('jobs', 'start_time', 'DESC'))
        else:
            job_items = db.get_vertex_list_joined(cls.COLLECTION_NAME, {"submissions": ("uuid", "submission")}, filter_map={"submissions": ('uuid', submission_uuid)}, sort_by=('jobs', 'start_time', 'DESC'))

        for job_item in job_items:
            del job_item['submission']['_id']
            del job_item['submission']['_key']
            del job_item['submission']['_rev']
            del job_item['submission']['base_dir']

            if job_item.get('primary', '') != '':
                file_data = db.get_vertex_by_match('kogia-graph', 'files', 'uuid', job_item['primary'])
                if file_data is not None:
                    job_item['primary_name'] = file_data['name']
                else:
                    job_item['primary_name'] = ""
            new_list.append(job_item)
        
        return new_list

    def __init__(self, db, uuid=None, id=None):
        super().__init__(self.COLLECTION_NAME, id)

        self._user = ""
        self._submission = None
        self._primary = None
        self._start_time = int(time.time())
        self._complete_time = 0
        self._complete = False
        self._error = []
        self._plugins = []
        self._uuid = uuid
        self._db = db
        self._arg_map = {}
        self._reports = []
        self._matches = []
        self._limit_to = []
        self._processes = []

    def add_limit_to_file(self, file_uuid):
        self._limit_to.append(file_uuid)

    def clear_file_limit(self):
        self._limit_to = []

    @property
    def limited_to(self):
        return self._limit_to

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

    def add_plugin(self, new_plugin, args=None):
        found = False
        for plugin in self._plugins:
            if plugin.__name__ == new_plugin.__name__:
                found = True
        
        if not found:
            self._plugins.append(new_plugin)
            if args is not None:
                self._arg_map[new_plugin.__name__] = args
            
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
            "submission": self._submission.uuid,
            "plugin_args": self._arg_map
        }

    def from_dict(self, pm, data_obj):
        self._uuid = data_obj.get('uuid', '')
        self._name = data_obj.get('name', '')
        self._primary = data_obj.get('primary', '')
        self._start_time = data_obj.get('start_time', 0)
        self._complete_time = data_obj.get('complete_time', 0)
        self._complete = data_obj.get('complete', False)
        self._error = data_obj.get('error', '')
        self._arg_map = data_obj.get('plugin_args', '')

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
        print(self._plugins)
        return copy.deepcopy(self._plugins)

    def get_initialized_plugin_list(self, pm):
        return_list = []
        plugin_class_list = self.get_plugin_list()
        for plugin_class in plugin_class_list:
            name = plugin_class.__name__
            if name in self._arg_map:
                return_list.append(pm.initialize_plugin(plugin_class, args=self._arg_map[name]))
            else:
                return_list.append(pm.initialize_plugin(plugin_class))
        return return_list

    def _save_reports(self):
        for report in self._reports:
            report.save(self._db)
            self.insert_edge(self._db, 'added_report', report.id)
            file_obj = SubmissionFile(uuid=report.file_uuid)
            file_obj.load(self._db)
            file_obj.insert_edge(self._db, 'has_report', report.id)

    def _save_matches(self):
        for match in self._matches:
            match.save(self._db)
            self.insert_edge(self._db, 'added_match', match.id)

    def _save_processes(self):
        for process in self._processes:
            process.save(self._db)
            self.insert_edge(self._db, 'has_process', process.id)

    def add_signature(self, plugin_name, name, file_obj, description, severity=None, metadata=None, events=None, syscalls=None):
        new_signature = Signature()
        new_signature.name = name
        new_signature.plugin_name = plugin_name
        if severity is not None:
            new_signature.severity = severity
        new_signature.load(self._db)
        if new_signature.id is None:
            new_signature.description = description

        new_match = SignatureMatch.new(new_signature, file_obj)
        if metadata is not None:
            pass

        self._matches.append(new_match)

    def add_report(self, report_name, file_obj, data):

        new_report = Report()
        new_report.value = data
        new_report.name = report_name
        new_report.file_uuid = file_obj.uuid

        self._reports.append(new_report)

    def add_process(self, proc_name, pid, file_obj=None):
        new_proc = None
        if file_obj is not None:
            is_primary = False
            if file_obj.uuid == self._primary:
                is_primary = True
            new_proc = Process.new(proc_name, pid, is_primary=is_primary, file=file_obj)
        else:
            new_proc = Process.new(proc_name, pid)
            
        self._processes.append(new_proc)
        return new_proc

    def get_reports(self, file_uuid=None):
        # Ensure any stored reports are saved
        self._save_reports()

        if file_uuid is None:
            return self.get_connected_to(self._db, 'reports', filter_edges=['added_report'])
        else:
            file_obj = SubmissionFile(uuid=file_uuid)
            file_obj.load(self._db)
            return file_obj.get_in_path(self._db, self.id, 1, ['has_report', 'added_report'], return_fields=['uuid', 'name'])

    def get_signatures(self, file_uuid=None):
        # Ensure any stored reports are saved
        self._save_matches()

        if file_uuid is None:
            return self.get_connected_to(self._db, 'signatures', filter_edges=['added_match', 'matched_signature'])
        else:
            file_obj = SubmissionFile(uuid=file_uuid)
            file_obj.load(self._db)
            return file_obj.get_in_path(self._db, self.id, 1, ['has_match', 'added_match'], return_fields=['uuid', 'name'])


    def get_processes(self):
        self._save_processes()
        return self.get_connected_to(self._db, 'processes', filter_edges=['has_process'])


    def save(self):
        self.save_doc(self._db, self.to_dict())
        self._submission.save(self._db)
        self._save_reports()
        self._save_matches()

    def load(self, pm):
        doc = self.load_doc(self._db, 'uuid', self._uuid)
        self.from_dict(pm, doc)

    def add_to_error(self, error_message):
        self._error.append(error_message)

    def _log(self, severity, log_name, message):
        self._db.insert("logs", {
            "severity": severity,
            "log_name": log_name,
            "message": message,
            "job_uuid": self._uuid,
            "log_time": int(time.time())
        })

    def error_log(self, log_name, message):
        self._log('error', log_name, message)

    def info_log(self, log_name, message):
        self._log('info', log_name, message)

    def warning_log(self, log_name, message):
        self._log('warning', log_name, message)

    def get_logs(self):
        return self._db.get_list_by_match("logs", "job_uuid", self._uuid)


