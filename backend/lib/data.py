import uuid
import os
import stat
import time
import hashlib
import copy
from enum import IntEnum
import logging

from .submission import SubmissionFile
from .db import ArangoConnection

from PIL import Image

from .db import DBNotUniqueError
from .objects import VertexObject, VertexObjectWithMetadata

logger = logging.getLogger(__name__)

class SIGNATURE_SEVERITY(IntEnum):
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
        self._extra = []


    @property
    def file_uuid(self):
        return self._file.uuid
    
    @property
    def extra(self):
        return copy.deepcopy(self._extra)
    
    def add_extra_data(self, extra_dict):
        # extra data is expected to to a dict
        
        for current_item in self._extra:
            if current_item == extra_dict:
                return
        self._extra.append(extra_dict)

    def to_dict(self, full=False):
        if self._uuid == "":
            self._gen_uuid()
        return_obj =  {
            "_key": self._uuid,
            "match_time": self._match_time,
            "extra": self._extra
        }
        if full:
            return_obj['signature'] = self._signature.to_dict()

        return return_obj

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('_key', '')
        self._match_time = data_obj.get('match_time', '')
        self._extra = data_obj.get('extra', [])
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
            document = self.load_doc(db, field='_key', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is not None:
            self.from_dict(document)

    def load_file(self, db, filestore):
        my_file_list = self.get_connected_to(db, 'files')
        if len(my_file_list) > 0:
            self._file = SubmissionFile(id=my_file_list[0]['_id'], filestore=filestore)
            self._file.from_dict(my_file_list[0])
    

    def load_signature(self, db):

        my_sig_list = self.get_connected_to(db, 'signatures', max=1)

        if len(my_sig_list) > 0:
            self._signature = Signature(id=my_sig_list[0]['_id'])
            self._signature.from_dict(my_sig_list[0])


    @property
    def signature(self):
        return self._signature
    
    @property
    def file(self):
        return self._file

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
            "_key": self._uuid,
            "uuid": self._uuid,
            "name": self.name,
            "description": self.description,
            "plugin": self.plugin_name,
            "severity": int(self.severity)
        }

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('_key', '')
        self.name = data_obj.get('name', '')
        self.description = data_obj.get('description', '')
        self.plugin_name = data_obj.get('plugin', '')
        self.severity = SIGNATURE_SEVERITY(int(data_obj.get('severity', 1)))

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
            document = self.load_doc(db, field='_key', value=self._uuid)
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
            "_key": self._uuid,
            "uuid": self._uuid,
            "value": self._value,
            "file_uuid": self._file_uuid,
            "name": self.name
        }

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('_key', '')
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
            document = self.load_doc(db, field='_key', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is not None:
            self.from_dict(document)
        else:
            self._uuid = None

class ExecInstance(VertexObjectWithMetadata):

    COLLECTION_NAME = 'exec_instance'

    @classmethod
    def new(cls, submission_uuid, module_name, run_os):
        new_cls = cls(uuid=str(uuid.uuid4()))
        new_cls.exec_module = module_name
        new_cls._run_os = run_os
        new_cls._submission_uuid = submission_uuid
        return new_cls

    def __init__(self, id=None, uuid=None):
        super().__init__(self.COLLECTION_NAME, 'has_instance_metadata', id)
        self._uuid = uuid
        self._submission_uuid = ""
        self._start_time = 0
        self._end_time = 0
        self.exec_module = ""
        self._run_os = ""
        self._processes = []
        self._syscall_counter = 0
        self._event_counter = 0
        self._network_comms = []
        self._network_comms_total = 0
        self._comm_counter = 1
        self._comm_stats = {}
        self._screenshots = []
        self._process_count = 0
        self._loaded_processes = False

    def to_dict(self, full=True):
        ret_dict = {
            "_key": self._uuid,
            "uuid": self._uuid,
            "submission_uuid": self._submission_uuid,
            "start_time": self._start_time,
            "end_time": self._end_time,
            "exec_module": self.exec_module,
            "run_os": self._run_os,
            "screenshots": self._screenshots,
            "process_count": self._process_count
        }
        if full:
            ret_dict["processes"] = []
            for proc in self._processes:
                ret_dict["processes"].append(proc.to_dict(get_children=True))
        return ret_dict

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('_key', '')
        self._submission_uuid = data_obj.get('submission_uuid', '')
        self._start_time = data_obj.get('start_time', 0)
        self._end_time = data_obj.get('end_time', 0)
        self.exec_module = data_obj.get('exec_module', '')
        self._run_os = data_obj.get('run_os', '')
        self._screenshots = data_obj.get('screenshots', [])
        if 'signature' in data_obj:
            self._signature = Signature(uuid=data_obj['signature'])


    def save(self, db):
        logger.debug("Saving exec instance %s", self._uuid)
        try:
            self.save_doc(db, self.to_dict(full=False))
        except DBNotUniqueError:
            pass

        if self._processes is not None:
            for process in self._processes:
                process.save(db)
                self.insert_edge(db, 'has_process', process.id)

        for networkcomm in self._network_comms:
            networkcomm.save(db)
            self.insert_edge(db, 'has_instance_netcomm', networkcomm.id, data={
                "comm_time": networkcomm.time
            })

        self.save_metadata(db)

    def load(self, db):
        document = {}
        if self.id is None:
            document = self.load_doc(db, field='_key', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is not None:
            self.from_dict(document)
        else:
            self._uuid = None
        

    def load_processes(self, db):
        items = self.get_connected_to(db, 'processes', filter_edges=['has_process'])
        process_count = 0
        for item in items:
            load_data = Process(id=item['_id'])
            load_data.from_dict(item)
            load_data.load_child_processes(db, load_event_count=True)
            load_data.load_events(db, count_only=True)
            self._processes.append(load_data)
            self._process_count += 1
            self._process_count += load_data.child_process_count
        self._loaded_processes = True

        
    def load_netcomms(self, db, as_dict=False, limit=30, skip=0, address_filter=None, port_filter=None):
        full_filter = None
        if address_filter is not None or port_filter is not None:

            port_filter_obj = None
            if port_filter is not None:
                port_filter_obj = (
                    'OR',
                    [
                        ('dest_port', port_filter),
                        ('src_port', port_filter),
                    ]
                )

            addr_filter_obj = None
            if address_filter is not None:
                addr_filter_obj = (
                    'OR',
                    [
                        ('dest_addr', address_filter),
                        ('src_addr', address_filter),
                    ]
                )
            
            if address_filter is not None and port_filter is not None:
                full_filter = ("AND", [port_filter_obj, addr_filter_obj])
            elif address_filter is not None:
                full_filter = addr_filter_obj
            elif port_filter is not None:
                full_filter = port_filter_obj

        self._network_comms_total = self.count_connected_to(db, NetworkComm.COLLECTION_NAME, filter_edges=['has_instance_netcomm'], filter_vertices=full_filter, direction='out', max=1)[0]
        time_key = 'comm_time'
        items = self.get_connected_to(db, NetworkComm.COLLECTION_NAME, filter_edges=['has_instance_netcomm'], filter_vertices=full_filter, direction='out', max=1, limit=limit, skip=skip, 
                                          sort_by=('has_instance_netcomm', time_key, 'ASC'), add_edges=True)
        
        if not as_dict:
            for item in items:
                load_data = NetworkComm(id=item['_id'])
                load_data.from_dict(item)
                if '_edge' in item:
                    load_data.time = item['_edge'][time_key]
                self._network_comms.append(load_data)
        else:
            for i in range(len(items)):
                if '_edge' in items[i]:
                    items[i]['time'] = items[i]['_edge'][time_key]
                    del items[i]['_edge']
            self._network_comms = items
        
        self._get_network_comm_stats(db)


    def add_process(self, proc_path, pid, command_line):
        new_proc = Process.new(proc_path, pid, command_line)
            
        self._processes.append(new_proc)
        return new_proc
    
    def add_network_comm(self, protocol, src_addr, src_port, dest_addr, dest_port, data, comm_time=None):
        new_comm = NetworkComm()
        new_comm.protocol = protocol
        new_comm.src_addr = src_addr
        new_comm.src_port = src_port
        new_comm.dest_addr = dest_addr
        new_comm.dest_port = dest_port
        new_comm.data = data

        if comm_time is not None:
            new_comm.time = comm_time
        else:
            new_comm.time = self._comm_counter
            self._comm_counter += 1
        
        self._network_comms.append(new_comm)
        return new_comm

    @property
    def network_comm_statistics(self):
        return self._comm_stats

    def _get_network_comm_stats(self, db):
        port_map = {}
        address_map = {}
        items = self.get_connected_to(db, NetworkComm.COLLECTION_NAME, filter_edges=['has_instance_netcomm'], direction='out', max=1)

        for item in items:
            src_port = 0
            dest_port = 0
            src_addr = ""
            dest_addr = ""
            src_addr = item['src_addr']
            src_port = int(item['src_port'])
            dest_addr = item['dest_addr']
            dest_port = int(item['dest_port'])
            
            if src_port != 0:
                if src_port not in port_map:
                    port_map[src_port] = 0
                port_map[src_port] += 1

            if dest_port != 0:
                if dest_port not in port_map:
                    port_map[dest_port] = 0
                port_map[dest_port] += 1

            if src_addr != "":
                if src_addr not in address_map:
                    address_map[src_addr] = 0
                address_map[src_addr] += 1

            if dest_addr != 0:
                if dest_addr not in address_map:
                    address_map[dest_addr] = 0
                address_map[dest_addr] += 1

        self._comm_stats = {
            "ports": port_map,
            "addresses": address_map
        }

    def add_screenshot(self, filestore, in_stream, format='png'):
        screenshot_name_base = f"screenshot-{len(self._screenshots)+1}-{self._uuid}"
        screenshot_name = f"{self._submission_uuid}:{screenshot_name_base}"
        thumb_name = f"{self._submission_uuid}:{screenshot_name_base}-t"
        image = Image.open(in_stream, formats=[format])
        image.thumbnail((300, 300))

        # Save thumbnail
        thumb_file = filestore.create_file(thumb_name)
        image.save(thumb_file, format=format)
        filestore.close_file(thumb_name, thumb_file)

        # Save original image
        screenshot_file = filestore.create_file(screenshot_name)
        in_stream.seek(0)
        screenshot_file.write(in_stream.read())
        filestore.close_file(screenshot_name, screenshot_file)

        self._screenshots.append(screenshot_name)

    @property
    def screenshots(self):
        return self._screenshots

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
    
    @property
    def processes(self):
        if not self._loaded_processes:
            raise ValueError("load_processes not called before accessing processes.")
        # return copy.deepcopy(self._processes)
        return self._processes
    
    @property
    def process_list(self):
        if not self._loaded_processes:
            raise ValueError("load_processes not called before accessing processes.")
        # return copy.deepcopy(self._processes)
        proc_list = []
        for process in self._processes:
            proc_list.append(process)
            proc_list += process.child_process_list 
        return proc_list

    @end_time.setter
    def end_time(self, new_time):
        self._end_time = new_time

    @property
    def network_comms(self):
        return self._network_comms
    
    @property
    def network_comms_total(self):
        return self._network_comms_total

class Event(VertexObject):
    
    COLLECTION_NAME = 'events'

    @classmethod
    def bulk_insert(cls, db, insert_objs):
        insert_events = []
        for event in insert_objs:
            if isinstance(event, Event) and event.id != None:
                insert_events.append(event.to_dict())

        return db.insert_bulk(Event.COLLECTION_NAME, insert_events, requery=False)

    def __init__(self, id=None, uuid=None):
        super().__init__(self.COLLECTION_NAME, id)
        self._uuid = uuid
        self._key = ""
        self._src = ""
        self._dest = ""
        self._data = ""
        self._time = 0
        self._success = True

    def _gen_uuid(self):
        my_uuid  = hashlib.sha256(
            (self._key).encode() + \
            (self._src).encode() + \
            (self._dest).encode() + \
            (self._data).encode()
        )
        self._uuid = my_uuid.hexdigest()

    def to_dict(self, full=True):
        self._gen_uuid()
        ret_dict = {
            "_key": self._uuid,
            "uuid": self._uuid,
            "key": self._key,
            "src": self._src,
            "dest": self._dest,
            "data": self._data,
            "success": self._success
        }
        if full:
            ret_dict['time'] = self._time
        return ret_dict

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('_key', '')
        self._key = data_obj.get('key', '')
        self._src = data_obj.get('src', '')
        self._dest = data_obj.get('dest', '')
        self._data = data_obj.get('data', '')
        self._data = data_obj.get('success', True)
        if 'signature' in data_obj:
            self._signature = Signature(uuid=data_obj['signature'])

    def save(self, db):
        try:
            self.save_doc(db, self.to_dict(full=False))
        except DBNotUniqueError:
            pass

    def load(self, db):
        document = {}
        if self.id is None:
            document = self.load_doc(db, field='_key', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is not None:
            self.from_dict(document)

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, new_key):
        self._key = new_key

    @property
    def src(self):
        return self._src

    @src.setter
    def src(self, new_src):
        self._src = new_src 

    @property
    def dest(self):
        return self._dest

    @dest.setter
    def dest(self, new_dest):
        self._dest = new_dest  

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        self._data = new_data 

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, new_time):
        self._time = new_time

    @property
    def success(self):
        return self._success

    @success.setter
    def success(self, new_success):
        self._success = new_success

class Process(VertexObjectWithMetadata):

    COLLECTION_NAME = 'processes'

    @classmethod
    def new(cls, proc_path, pid, command_line):
        new_cls = cls(uuid=str(uuid.uuid4()))
        new_cls._path = proc_path
        new_cls._command_line = command_line
        new_cls._pid = pid
        return new_cls


    def __init__(self, id=None, uuid=None):
        super().__init__(self.COLLECTION_NAME, 'has_process_metadata', id)
        self._uuid = uuid
        self._pid = 0
        self._parent_pid = 0
        self._path = ""
        self._command_line = ""
        self._start_time = 0
        self._end_time = 0
        self._syscalls = []
        self._events = []
        self._event_total = -1
        self._event_total = 0
        self._events_synced = False
        self._child_processes = []
        self._event_counter = 1
        self._libs = []
        self._syscalls = []
        self._syscall_total = 0
        self._syscalls_synced = False

    @property
    def pid(self):
        return self._pid
    
    @property
    def parent_pid(self):
        return self._parent_pid

    @parent_pid.setter
    def parent_pid(self, new_parent_pid):
        self._parent_pid = int(new_parent_pid)
    
    @property
    def path(self):
        return self._path
    
    @property
    def command_line(self):
        return self._command_line
    
    def to_dict(self, get_children=True):
        ret_dict = {
            "_key": self._uuid,
            "uuid": self._uuid,
            "pid": self._pid,
            "parent_pid": self._parent_pid,
            "path": self._path,
            "command_line": self._command_line,
            "start_time": self._start_time,
            "end_time": self._end_time,
            "libraries": self._libs,
            "event_count": self.event_count,
        }
        if get_children:
            ret_dict["child_processes"] = []
            for child_proc in self._child_processes:
                ret_dict["child_processes"].append(child_proc.to_dict(get_children=True))
        return ret_dict

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('_key', '')
        self._pid = data_obj.get('pid', 0)
        self._path = data_obj.get('path', '')
        self._command_line = data_obj.get('command_line', '')
        self._start_time = data_obj.get('start_time', 0)
        self._end_time = data_obj.get('end_time', 0)
        self._parent_pid = data_obj.get('parent_pid', 0)
        
        
        if 'libraries' in data_obj:
            for shared_lib in data_obj['libraries']:
                self.add_shared_lib(shared_lib)

        if 'child_processes' in data_obj:
            for item in data_obj['child_processes']:
                add_proc = Process(uuid=item['_key'])
                add_proc.from_dict(item)
                add_proc.parent_pid = self._pid
                self._child_processes.append(add_proc)

    def save(self, db):
        logger.debug("Saving process %s, PID=%s", self._uuid, str(self._pid))
        try:
            self.save_doc(db, self.to_dict(get_children=False))
        except DBNotUniqueError:
            pass

        if self._child_processes is not None:
            for process in self._child_processes:
                if isinstance(process, Process):
                    process.save(db)
                    self.insert_edge(db, 'is_child_of', process.id)

        self.save_events(db)
        self.save_metadata(db)
        self.save_syscalls(db)

    def save_events(self, db):
        if self._events_synced:
            return
        
        # Save events in bulk, then add edges after
        Event.bulk_insert(db, self._events)

        for event in self._events:
            if isinstance(event, Event):
                # Yeah, this will be slow, but we want to store the time of the event too
                # event.save(db)
                self.insert_edge(db, 'has_event', event.id, data={
                    "event_time": event.time
                })

    def save_syscalls(self, db):
        if self._syscalls_synced:
            return
        logger.debug("Saving syscalls for process %s, PID=%s", self._uuid, str(self._pid))
        # Insert syscalls
        insert_syscalls = []
        for syscall in self._syscalls:
            if "_id" not in syscall:
                insert_syscalls.append(syscall)

        # Syscalls will not have _key, so we need to get the ids from the insert
        new_ids = db.insert_bulk('syscalls', insert_syscalls, requery=False)
        self.insert_edge_bulk(db, 'has_syscall', 'syscalls', new_ids)

        # Since we select syscalls to insert based on _id, we need to reload all the syscalls
        # to ensure we don't insert multiple times
        self._syscalls = []
        self.load_syscalls(db)
        self._syscalls_synced = True

    def load(self, db):
        document = {}
        if self.id is None:
            document = self.load_doc(db, field='_key', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is not None:
            self.from_dict(document)

    def load_child_processes(self, db, get_children=True, load_event_count=False):
        self._child_processes = []
        items = self.get_connected_to(db, 'processes', filter_edges=['is_child_of'], direction='out', max=1)
        for item in items:
            load_data = Process(id=item['_id'])
            load_data.from_dict(item)
            load_data.parent_pid = self._pid
            if get_children:
                load_data.load_child_processes(db, get_children=get_children, load_event_count=load_event_count)
            if load_event_count:
                load_data.load_events(db, count_only=True)
            self._child_processes.append(load_data)

    def load_events(self, db, as_dict=False, limit=0, skip=0, count_only=False):
        self._events = []
        if not count_only:
            items = self.get_connected_to(db, 'events', filter_edges=['has_event'], direction='out', max=1, limit=limit, skip=skip, 
                                          sort_by=('has_event', 'event_time', 'ASC'), add_edges=True)
            
            if not as_dict:
                for item in items:
                    load_data = Event(id=item['_id'])
                    load_data.from_dict(item)
                    if '_edge' in item:
                        load_data.time = item['_edge']['event_time']
                    self._events.append(load_data)
                    self._event_counter += 1
                    self._events_synced = True
            else:
                for i in range(len(items)):
                    if '_edge' in items[i]:
                        items[i]['time'] = items[i]['_edge']['event_time']
                        del items[i]['_edge']
                self._events = items
                self._events_synced = True
        
        result = self.count_connected_to(db, 'events', filter_edges=['has_event'], direction='out', max=1)
        if len(result) > 0:
            self._event_total = result[0]
        else:
            self._event_total = 0
        self._event_counter = self._event_total
    
    def load_syscalls(self, db : ArangoConnection, skip=0, limit=20):
        self._syscall_total = self.count_connected_to(db, 'syscalls', filter_edges=['has_syscall'], direction='out', max=1)[0]
        self._syscalls = self.get_connected_to(db, 'syscalls', filter_edges=['has_syscall'], max=1, 
                                               direction="out", limit=limit, skip=skip, sort_by=('syscalls', 'timestamp', "ASC"))
        self._syscalls_synced = True

    def add_child_process(self, proc_path, pid, command_line):
        child_proc = Process.new(proc_path, pid, command_line)
        child_proc.parent_pid = self._pid
        self._child_processes.append(child_proc)
        return child_proc

    def add_event(self, event_key, event_src=None, event_dest=None, event_data=None, event_time=None, event_success=True):
        new_event = Event()
        new_event.key = event_key
        if event_src:
            new_event.src = event_src
        if event_dest:
            new_event.dest = event_dest
        if event_data:
            new_event.data = event_data

        new_event.success = event_success
        if event_time is None:
            new_event.time = self._event_counter
            self._event_counter += 1
        else:
            new_event.time = event_time

        self._events.append(new_event)
        self._events_synced = False
        return new_event
        
    def add_shared_lib(self, lib_path):
        self._libs.append(lib_path)
    
    def add_syscall(self, name, arg_list, return_code, timestamp, tid):
        new_syscall = {
            "name": name,
            "args": arg_list,
            "return_code": return_code,
            "timestamp": timestamp,
            "tid": tid
        }
        self._syscalls.append(new_syscall)
        self._syscalls_synced = False

    @property
    def events(self):
        """
        All events from the process.
        WARNING: Do not expect edits done here to be saved!
        """
        return self._events
    
    @property
    def event_total(self):
        return self._event_total
    
    @property
    def syscalls(self):
        """
        All syscalls from the process.
        WARNING: Do not expect edits done here to be saved!
        """
        return self._syscalls
    
    @property
    def syscall_total(self):
        return self._syscall_total

    @property
    def event_count(self):
        if self._event_total == -1:
            return len(self._events)
        else:
            return self._event_total
    
    @property
    def child_processes(self):
        return self._child_processes
    
    @property
    def child_process_list(self):
        """
        Creates a flattened list of processes with the process and its child processes
        """
        proc_list = []
        for child_proc in self._child_processes:
            proc_list.append(child_proc)
            proc_list += child_proc.child_process_list
        return proc_list
    
    @property
    def child_process_count(self):
        count = 0
        for subproc in self._child_processes:
            count += 1
            count += subproc.child_process_count
        return count

    @property
    def uuid(self):
        return self._uuid
    
    def run_on_process_tree(self, func, context):
        func(self, context)
        if len(self._child_processes) > 0:
            for child_proc in self._child_processes:
                child_proc.run_on_process_tree(func, context)

class NetworkComm(VertexObject):

    COLLECTION_NAME = 'networkcomm'

    def __init__(self, id=None, uuid=None):
        super().__init__(self.COLLECTION_NAME, id)
        self._uuid = uuid
        self._protocol = ""
        self._src_addr = ""
        self._src_port = ""
        self._dest_addr = ""
        self._dest_port = ""
        self._data = ""
        self._time = 0

    def _gen_uuid(self):
        my_uuid  = hashlib.sha256(
            self.__str__().encode()
        )
        self._uuid = my_uuid.hexdigest()

    def __str__(self):
        return f"{self._protocol}|{self._src_addr}:{self._src_port}|{self._dest_addr}:{self._dest_port}|{self._data}"

    def to_dict(self, full=True):
        self._gen_uuid()
        ret_dict = {
            "_key": self._uuid,
            "uuid": self._uuid,
            "protocol": self._protocol,
            "src_addr": self._src_addr,
            "src_port": self._src_port,
            "dest_addr": self._dest_addr,
            "dest_port": self._dest_port,
            "data": self._data,
        }
        if full:
            ret_dict['time'] = self._time
        return ret_dict

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('_key', '')

        self._protocol = data_obj.get('protocol', '')
        self._src_addr = data_obj.get('src_addr', '')
        self._src_port = int(data_obj.get('src_port', 0))
        self._dest_addr = data_obj.get('dest_addr', '')
        self._dest_port = int(data_obj.get('dest_port', 0))

        self._data = data_obj.get('data', '')

    def save(self, db):
        try:
            self.save_doc(db, self.to_dict(full=False))
        except DBNotUniqueError:
            pass

    def load(self, db):
        document = {}
        if self.id is None:
            document = self.load_doc(db, field='_key', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is not None:
            self.from_dict(document)

    @property
    def uuid(self):
        return self._uuid

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, new_key):
        self._key = new_key

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, new_protocol):
        self._protocol = new_protocol 

    @property
    def src_addr(self):
        return self._src_addr

    @src_addr.setter
    def src_addr(self, new_src_addr):
        self._src_addr = new_src_addr

    @property
    def src_port(self):
        return self._src_port

    @src_port.setter
    def src_port(self, new_src_port):
        self._src_port = int(new_src_port)

    @property
    def dest_addr(self):
        return self._dest_addr

    @dest_addr.setter
    def dest_addr(self, new_dest_addr):
        self._dest_addr = new_dest_addr

    @property
    def dest_port(self):
        return self._dest_port

    @dest_port.setter
    def dest_port(self, new_dest_port):
        self._dest_port = int(new_dest_port)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        self._data = new_data 

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, new_time):
        self._time = new_time