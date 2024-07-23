from multiprocessing.sharedctypes import Value
import time
import uuid
import copy
import logging

from backend.lib.submission import Submission, SubmissionFile
from backend.lib.objects import VertexObject, CollectionObject, FilestoreObject
from backend.lib.data import Process, Signature, SignatureMatch, Report, ExecInstance, SIGNATURE_SEVERITY, Event
from .helpers import safe_uuid

logger = logging.getLogger(__name__)

class Job(VertexObject):
    """Object representing a Job, which runs a series of plugins on a Submission.

    This object performs a little differently, as it contains its own database object instead
    of it being passed to it.
    """

    COLLECTION_NAME = 'jobs'

    @classmethod
    def new(cls, submission, primary, db, filestore):
        new_cls = cls(db, filestore, uuid=str(uuid.uuid4()))
        new_cls._submission = submission
        new_cls._primary = primary
        # Ensure files and their metadata are all loaded
        new_cls._submission.load_files(db, filestore)
        for file in new_cls._submission.files:
            file.load_metadata(db)

        return new_cls

    @classmethod
    def list_dict(cls, db, skip=0, limit=20, submission_uuid=None):
        new_list = []
        job_items = []
        if submission_uuid is None:
            job_items = db.get_vertex_list_joined(cls.GRAPH_NAME, cls.COLLECTION_NAME, {"submissions": ("_key", "submission")}, sort_by=('jobs', 'start_time', 'DESC'), skip=skip, limit=limit)
        else:
            job_items = db.get_vertex_list_joined(cls.GRAPH_NAME, cls.COLLECTION_NAME, {"submissions": ("_key", "submission")}, filter_map={"submissions": ('_key', submission_uuid)}, sort_by=('jobs', 'start_time', 'DESC'), skip=skip, limit=limit)

        for job_item in job_items:
            del job_item['submission']['_id']
            job_item['submission']['uuid'] = job_item['submission']['_key']
            del job_item['submission']['_rev']

            del job_item['_id']
            job_item['uuid'] = job_item['_key']
            del job_item['_rev']

            if job_item.get('primary', '') != '':
                file_data = db.get_vertex_by_match(cls.GRAPH_NAME, 'files', '_key', job_item['primary'])
                if file_data is not None:
                    job_item['primary_name'] = file_data['name']
                else:
                    job_item['primary_name'] = ""
            new_list.append(job_item)
        
        total_len = 0
        if submission_uuid is None:
            total_len = db.get_vertex_list_sorted(cls.GRAPH_NAME, cls.COLLECTION_NAME, 'start_time', 'DESC', length_only=True)[0]
        else:
            total_len = db.get_vertex_list_joined(cls.GRAPH_NAME, cls.COLLECTION_NAME, {"submissions": ("_key", "submission")}, 
                                                  filter_map={"submissions": ('_key', submission_uuid)}, 
                                                  sort_by=('jobs', 'start_time', 'DESC'),
                                                  length_only=True
                                                )[0]

        return total_len, new_list

    def __init__(self, db, filestore, uuid=None, id=None):
        super().__init__(self.COLLECTION_NAME, id)

        self._user = ""
        self._submission = None
        self._primary = None
        self._start_time = int(time.time())
        self._complete_time = 0
        self._complete = False
        self._error = []
        self._plugins = []
        self._uuid = safe_uuid(uuid)
        self._db = db
        self._filestore = filestore
        self._arg_map = {}
        self._reports = []
        self._matches = []
        self._limit_to = []
        self._exec_instances = []
        self._score = 0

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
    def filestore(self):
        return self._filestore

    @property
    def primary(self):
        return self._primary
    
    def get_primary_file(self) -> SubmissionFile:
        primary_file = self._submission.get_file(uuid=self._primary)
        primary_file.load(self._db)
        return primary_file

    @property
    def submission(self):
        return self._submission

    @property
    def score(self):
        return self._score

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
            "_key": self._uuid,
            "uuid": self._uuid,
            "user": self._user,
            "primary": self._primary,
            "start_time": self._start_time,
            "complete_time": self._complete_time,
            "complete": self._complete,
            "error": self._error,
            "plugins": plugin_list,
            "submission": self._submission.uuid,
            "plugin_args": self._arg_map,
            "limit_to": self._limit_to,
            "score": self._score
        }

    def from_dict(self, pm, data_obj):
        self._uuid = data_obj.get('_key', '')
        self._name = data_obj.get('name', '')
        self._primary = data_obj.get('primary', '')
        self._start_time = data_obj.get('start_time', 0)
        self._complete_time = data_obj.get('complete_time', 0)
        self._complete = data_obj.get('complete', False)
        self._error = data_obj.get('error', '')
        self._arg_map = data_obj.get('plugin_args', '')
        self._limit_to = data_obj.get('limit_to', [])
        self._score = data_obj.get('score', 0)

        if 'submission' in data_obj:
            load_sub = Submission(uuid=data_obj['submission'])
            load_sub.load(self._db)
            self._submission = load_sub
        else:
            self._submission = None


        if 'plugins' in data_obj:
            self._plugins = []
            for item in data_obj['plugins']:
                self._plugins.append(pm.get_plugin(item))


    def get_plugin_list(self):
        return copy.deepcopy(self._plugins)
    
    @property
    def plugins(self):
        output = {}
        for plugin in self._plugins:
            if plugin.classname() in self._arg_map:
                output[plugin.classname()] = self._arg_map[plugin.classname()]
            else:
                output[plugin.classname()] = ""
        return output

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

    def save_exec_instances(self):
        for exec_instance in self._exec_instances:
            exec_instance.save(self._db)
            self.insert_edge(self._db, 'has_exec_instance', exec_instance.id)

    def add_signature(self, plugin_name, name, file_obj, description, severity=None, metadata=None, events=None, syscalls=None):

        # Ignore any duplicates
        for match_item in self._matches:
            
            if match_item.signature is None:
                match_item.load_signature(self._db)
            if match_item.signature.name == name and match_item.signature.plugin_name == plugin_name:
                return match_item
  
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
        return new_match

    def add_report(self, report_name, file_obj, data):

        new_report = Report()
        new_report.value = data
        new_report.name = report_name
        new_report.file_uuid = file_obj.uuid

        self._reports.append(new_report)

    def add_exec_instance(self, module_name, run_os):
        new_exec_instance = ExecInstance.new(self._submission.uuid, module_name, run_os)
        self._exec_instances.append(new_exec_instance)
        return new_exec_instance

    def get_reports(self, file_uuid=None):
        # Ensure any stored reports are saved
        self._save_reports()

        ret_reports = []
        if file_uuid is None:
            ret_reports = self.get_connected_to(self._db, 'reports', filter_edges=['added_report'])
        else:
            file_obj = SubmissionFile(uuid=file_uuid)
            file_obj.load(self._db)
            ret_reports_paths = file_obj.get_connected_to(self._db, self.id, filter_edges=['has_report', 'added_report'], return_path=True)

        
            for ret_report_paths in ret_reports_paths:
                ret_report = ret_report_paths['vertices'][1]
                
                ret_report['uuid'] = ret_report['_key']
                del ret_report['_key']
                ret_reports.append(ret_report)
                
        return ret_reports

    def get_matches(self, file_uuid=None):
        return_list = []
        for match_item in self._matches:
            
            if match_item.signature is None:
                match_item.load_signature(self._db)
            print(match_item.signature.name)
            # if match_item.file is None:
            #     match_item.load_file(self._db, self._filestore)
            if file_uuid is not None:
                if match_item.file_uuid == file_uuid:
                    return_list.append(match_item)
            else:
                return_list.append(match_item)
        return self._matches

    def get_signatures(self, file_uuid=None, as_obj=False):
        # Ensure any stored reports are saved
        self._save_matches()

        ret_signatures = []
        if file_uuid is None:
            ret_signatures = self.get_connected_to(self._db, 'signatures', filter_edges=['added_match', 'matched_signature'])
        else:
            file_obj = SubmissionFile(uuid=file_uuid)
            file_obj.load(self._db)
            ret_signatures_paths = file_obj.get_connected_to(self._db, self.id, filter_edges=['has_match', 'added_match'], return_path=True)
            for path_item in ret_signatures_paths:
                ret_signatures.append(path_item['vertices'][1])

        for ret_sig in ret_signatures:
            del ret_sig['_key']
        if not as_obj:
            return ret_signatures
        else:
            return_objs = []
            for signature in ret_signatures:
                new_obj = Signature(id=signature['_id'])
                new_obj.from_dict(signature)
                return_objs.append(new_obj)
            return return_objs

    def get_exec_instances(self, as_obj=False):
        self.save_exec_instances()
        exec_instances = self.get_connected_to(self._db, 'exec_instance', filter_edges=['has_exec_instance'])
        if not as_obj:
            return exec_instances
        return_objs = []
        for instance in exec_instances:
            new_obj = ExecInstance(id=instance['_id'])
            new_obj.from_dict(instance)
            new_obj.load_processes(self._db)
            return_objs.append(new_obj)
        return return_objs

    def add_screenshot(self, exec_instance : ExecInstance, in_stream, format='png'):
        exec_instance.add_screenshot(self._filestore, in_stream, format=format)

    def generate_export_file(self, filename, export_plugin, export_type, creator):
        # We don't care about duplicates
        new_export = ExportFile.new(self._filestore, self._db, self, filename, export_plugin, creator)
        new_export.file_type = export_type
        return new_export

    def update_score(self):

        # total_matches = 0
        # severity_map = {
        #     SIGNATURE_SEVERITY.INFO: 0,
        #     SIGNATURE_SEVERITY.CAUTION: 0,
        #     SIGNATURE_SEVERITY.SUSPICIOUS: 0,
        #     SIGNATURE_SEVERITY.MALICIOUS: 0
        # }
        # severity_weights = {
        #     SIGNATURE_SEVERITY.INFO: 0.02,
        #     SIGNATURE_SEVERITY.CAUTION: 0.13,
        #     SIGNATURE_SEVERITY.SUSPICIOUS: 0.25,
        #     SIGNATURE_SEVERITY.MALICIOUS: 0.60
        # }

        # signatures = self.get_signatures()
        # if len(signatures) == 0:
        #     return
        # for signature in signatures:
        #     severity_map[SIGNATURE_SEVERITY(int(signature['severity']))] += 1
        #     total_matches += 1

        # weighted_total = 0
        # for severity in severity_weights:
        #     weight = severity_weights[severity]
        #     weighted_total += (weight * severity_map[severity])

        # self._score = (weighted_total / total_matches) * 100

        severity_weights = {
            SIGNATURE_SEVERITY.INFO: 0.5,
            SIGNATURE_SEVERITY.CAUTION: 3,
            SIGNATURE_SEVERITY.SUSPICIOUS: 6,
            SIGNATURE_SEVERITY.MALICIOUS: 10
        }

        signatures = self.get_signatures()
        if len(signatures) == 0:
            return
        for signature in signatures:
            self._score += severity_weights[SIGNATURE_SEVERITY(int(signature['severity']))]


        if self._score > 100.0:
            self._score = 100.0

        

    def save(self):
        self.update_score()

        self.save_doc(self._db, self.to_dict())
        self._submission.save(self._db)
        self._save_reports()
        self._save_matches()
        self.save_exec_instances()

    def load(self, pm):
        doc = self.load_doc(self._db, '_key', self._uuid)
        self.from_dict(pm, doc)
        self._submission.load(self._db)
        self._submission.load_files(self._db, self._filestore)
        

    def load_matches(self):
        # Load matches
        matches_list = self.get_connected_to(self._db, 'signature_matches', filter_edges=['added_match'])
        for match in matches_list:
            load_match = SignatureMatch(id=match['_id'])
            load_match.from_dict(match)
            load_match.load_signature(self._db)
            self._matches.append(load_match)
        # print(self._matches)

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

    def get_logs(self, skip=0, limit=30):
        count = len(self._db.get_list_by_match("logs", "job_uuid", self._uuid))
        return count, self._db.get_list_by_match("logs", "job_uuid", self._uuid, skip=skip, limit=limit)



class ExportFile(CollectionObject, FilestoreObject):

    COLLECTION_NAME = 'export_file'

    @classmethod
    def new(cls, filestore, db, job, filename, export_plugin, creator):
        new_cls = cls(uuid=str(uuid.uuid4()))
        new_cls._export_plugin = export_plugin
        new_cls._creator = creator
        new_cls._job = job
        new_cls._db = db

        # Private in FilestoreObject
        new_cls._name = filename
        new_cls._filestore = filestore
        new_cls._file_id = f"EXPORTS:{filename}-{new_cls.uuid}"
        return new_cls
    
    def __init__(self, uuid=None, id=None, pm=None, filestore=None, job_uuid=None, db=None):
        CollectionObject.__init__(self, self.COLLECTION_NAME, id)
        FilestoreObject.__init__(self, filestore, "", "")
        # super().__init__(self.COLLECTION_NAME, id=id)

        self._name = ""
        self._uuid = safe_uuid(uuid)

        self._db = db
        self._filestore = filestore

        if job_uuid is not None:
            self._job = Job(self._db, self._filestore, uuid=safe_uuid(job_uuid))
            self._job.load(pm)
        
        self._export_plugin = None
        self._creator = None
        self._file_id = ""
        self._hash = ""

        self._handle = None

        self.file_type = ""

        self._signatures = []
        self._file_filters = []
        self._event_filters = {}
        self._syscall_filters = {}
        self._network_filters = {}

    # def __del__(self):
    #     self.close_file()

    def to_dict(self):
        return {
            "_key": self._uuid,
            "uuid": self._uuid,
            "job_uuid": self._job.uuid,
            "name": self._name,
            "file_id": self._file_id,
            "export_plugin": self._export_plugin,
            "creator": self._creator,
            "hash": self._hash,
            "filetype": str(self.file_type)
        }

    def from_dict(self, data_obj, pm):
        self._uuid = data_obj.get('_key', '')
        job_uuid = data_obj.get('job_uuid', '')
        if job_uuid != '':
            self._job = Job(self._db, self._filestore, uuid=safe_uuid(job_uuid))
            self._job.load(pm)
        self._name = data_obj.get('name', '')
        self._file_id = data_obj.get('file_id', '')
        self._export_plugin = data_obj.get('export_plugin', None)
        self._creator = data_obj.get('creator', None)
        self._hash = data_obj.get('hash', '')
        self.file_type = data_obj.get('filetype', '')

    def save(self):
        self.save_doc(self._db, self.to_dict())

    def load(self, pm):
        document = {}
        if self.id is None:
            document = self.load_doc(self._db, field='_key', value=self._uuid)
        else:
            document = self.load_doc(self._db)

        if document is not None:
            self.from_dict(document, pm)
        else:
            self._uuid = None

    def set_event_filter(self, new_filter):
        if not isinstance(new_filter, dict):
            raise ValueError("Filter must be a dict")
        self._event_filters = new_filter

    def set_network_filter(self, new_filter):
        if not isinstance(new_filter, dict):
            raise ValueError("Filter must be a dict")
        self._network_filters = new_filter

    def set_file_filter(self, new_filter):
        if not isinstance(new_filter, list):
            raise ValueError("Filter must be a list")
        self._file_filters = new_filter

    def has_files(self):
        return len(self._file_filters) > 0
    
    def has_network(self):
        return len(self._network_filters) > 0

    @property
    def uuid(self):
        return self._uuid

    @property
    def name(self):
        return self._name
    
    def signatures(self):
        signature_list = self._job.get_signatures(as_obj=True)

        signature_list.sort(key=lambda x: x.severity, reverse=True)

        for signature in signature_list:
            yield signature

    def files(self):

        # We need to load files from the submission
        # otherwise we miss the "dropped" connection from the edges

        for file_obj in self._job.submission.files:
            if file_obj.uuid in self._file_filters:
                yield file_obj

    def events(self):
        for instance_uuid in self._event_filters:
            exec_instance = ExecInstance(uuid=instance_uuid)
            exec_instance.load(self._db)
            # Skip if we couldn't load execution instance
            if exec_instance.uuid is None:
                continue
            

            exec_inst_dict = self._event_filters[instance_uuid]

            # Yield once with just the execution instance if told not to produce
            # any processes
            if len(exec_inst_dict.keys()) == 0:
                yield exec_instance, None, None
                return

            process_list = []
            all_processes = False
            all_events = False

                     
            if len(exec_inst_dict.keys()) == 1 and "*" in exec_inst_dict:
                exec_instance.load_processes(self._db)
                process_list = exec_instance.process_list
                all_processes = True
            else:
                for proc_uuid in self._event_filters[instance_uuid].keys():
                    process = Process(uuid=proc_uuid)
                    process.load(self._db)
                    process.load_child_processes(self._db)
                    if process.uuid is None:
                        continue
                    process_list.append(process)
                
                

            for process in process_list:     
                process_dict_list = []
                
                if not all_processes:
                    process_dict_list = self._event_filters[instance_uuid][process.uuid]
                else:
                    process_dict_list = self._event_filters[instance_uuid]["*"]

                if len(process_dict_list) == 0:
                    yield exec_instance, process, None
                    return

                event_list = []
                if len(process_dict_list) == 1 and process_dict_list[0] == "*":
                    process.load_events(self._db)
                    event_list = process.events
                else:
                    for event_uuid in process_dict_list:
                        event = Event(uuid=event_uuid)
                        event.load(self._db)
                        event_list.append(event)

                for event in event_list:
                    yield exec_instance, process, event
    
    def network_comms(self):
        exec_instances = self._job.get_exec_instances(as_obj=True)

        for exec_inst in exec_instances:
            if not exec_inst.uuid in self._network_filters:
                continue
            exec_inst.load_netcomms(self._db)
            for network_comm in exec_inst.network_comms:
                if self._network_filters[exec_inst.uuid] == "*" or network_comm.uuid in self._network_filters[exec_inst.uuid]:
                    yield exec_inst, network_comm
            