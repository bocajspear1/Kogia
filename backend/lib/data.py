import uuid
import os
import stat
import time
import hashlib
from enum import Enum

from .submission import SubmissionFile
from .db import ArangoConnection


from .db import DBNotUniqueError
from .objects import VertexObject, VertexObjectWithMetadata

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
            "_key": self._uuid,
            "match_time": self._match_time,
        }

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('_key', '')
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
            document = self.load_doc(db, field='_key', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is not None:
            self.from_dict(document)

    def load_file(self, db, filestore):
        my_file_list = self.get_connected_to(db, 'has_match')
        if len(my_file_list) > 0:
            self._file = SubmissionFile(id=my_file_list[0]['_id'], filestore=filestore)
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
            "_key": self._uuid,
            "uuid": self._uuid,
            "name": self.name,
            "description": self.description,
            "plugin": self.plugin_name,
            "severity": str(self.severity)
        }

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('_key', '')
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
    def new(cls, module_name, run_os):
        new_cls = cls(uuid=str(uuid.uuid4()))
        new_cls.exec_module = module_name
        new_cls._run_os = run_os
        return new_cls

    def __init__(self, id=None, uuid=None):
        super().__init__(self.COLLECTION_NAME, 'has_instance_metadata', id)
        self._uuid = uuid
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

    def to_dict(self, full=True):
        ret_dict = {
            "_key": self._uuid,
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
        self._uuid = data_obj.get('_key', '')
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
        for item in items:
            load_data = Process(id=item['_id'])
            load_data.from_dict(item)
            load_data.load_child_processes(db, load_event_count=True)
            load_data.load_events(db, count_only=True)
            self._processes.append(load_data)
        
    def load_netcomms(self, db, as_dict=False, limit=30, skip=0):
        self._network_comms_total = self.count_connected_to(db, NetworkComm.COLLECTION_NAME, filter_edges=['has_instance_netcomm'], direction='out', max=1)[0]
        time_key = 'comm_time'
        items = self.get_connected_to(db, NetworkComm.COLLECTION_NAME, filter_edges=['has_instance_netcomm'], direction='out', max=1, limit=limit, skip=skip, 
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

    @property
    def network_comms(self):
        return self._network_comms
    
    @property
    def network_comms_total(self):
        return self._network_comms_total

class Event(VertexObject):
    
    def __init__(self, id=None, uuid=None):
        super().__init__('events', id)
        self._uuid = uuid
        self._key = ""
        self._src = ""
        self._dest = ""
        self._data = ""
        self._time = 0

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
        self._path = ""
        self._command_line = ""
        self._start_time = 0
        self._end_time = 0
        self._syscalls = []
        self._events = []
        self._event_count = -1
        self._event_total = 0
        self._child_processes = []
        self._event_counter = 1
        self._libs = []
        self._syscalls = []
        self._syscall_total = 0

    @property
    def pid(self):
        return self._pid
    
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
            "path": self._path,
            "command_line": self._command_line,
            "start_time": self._start_time,
            "end_time": self._end_time,
            "libraries": self._libs,
            "event_count": self.event_count
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
        
        
        if 'libraries' in data_obj:
            for shared_lib in data_obj['libraries']:
                self.add_shared_lib(shared_lib)

        if 'child_processes' in data_obj:
            for item in data_obj['child_processes']:
                add_proc = Process(uuid=item['_key'])
                add_proc.from_dict(item)
                self._child_processes.append(add_proc)

    def save(self, db):
        try:
            self.save_doc(db, self.to_dict(get_children=False))
        except DBNotUniqueError:
            pass

        if self._child_processes is not None:
            for process in self._child_processes:
                if isinstance(process, Process):
                    process.save(db)
                    self.insert_edge(db, 'is_child_of', process.id)

        # Save events
        for event in self._events:
            if isinstance(event, Event):
                # Yeah, this will be slow, but we want to store the time of the event too
                event.save(db)
                self.insert_edge(db, 'has_event', event.id, data={
                    "event_time": event.time
                })

        self.save_metadata(db)

        self.save_syscalls(db)
        

    def save_syscalls(self, db):
        # Insert syscalls
        insert_syscalls = []
        for syscall in self._syscalls:
            if "_id" not in syscall:
                insert_syscalls.append(syscall)

        # Syscalls will not have _key, so we need to get the ids from the insert
        new_ids = db.insert_bulk('syscalls', insert_syscalls, requery=False)
        self.insert_edge_bulk(db, 'has_syscall', 'syscalls', new_ids)

        # Since we select syscalls to insert based on _id, we need to reload all the syscalls
        # to ensur ewe don't insert multiple times
        self._syscalls = []
        self.load_syscalls(db)

    def load(self, db):
        document = {}
        if self.id is None:
            document = self.load_doc(db, field='_key', value=self._uuid)
        else:
            document = self.load_doc(db)

        if document is not None:
            self.from_dict(document)

    def load_child_processes(self, db, get_children=True, load_event_count=False):
        items = self.get_connected_to(db, 'processes', filter_edges=['is_child_of'], direction='out', max=1)
        for item in items:
            load_data = Process(id=item['_id'])
            load_data.from_dict(item)
            if get_children:
                load_data.load_child_processes(db, get_children=get_children, load_event_count=load_event_count)
            if load_event_count:
                load_data.load_events(db, count_only=True)
            self._child_processes.append(load_data)

    def load_events(self, db, as_dict=False, limit=0, skip=0, count_only=False):
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
            else:
                for i in range(len(items)):
                    if '_edge' in items[i]:
                        items[i]['time'] = items[i]['_edge']['event_time']
                        del items[i]['_edge']
                self._events = items

            count_result = self.count_connected_to(db, 'events', filter_edges=['has_event'], direction='out', max=1)
            if len(count_result) > 0:
                total_count = count_result[0]
            else:
                total_count = 0

            self._event_total = total_count

            if limit > 0:
                self._event_counter = total_count
        else:
            result = self.count_connected_to(db, 'events', filter_edges=['has_event'], direction='out', max=1)
            if len(result) > 0:
                self._event_count = result[0]
            else:
                self._event_count = 0
    
    def load_syscalls(self, db : ArangoConnection, skip=0, limit=20):
        self._syscall_total = self.count_connected_to(db, 'syscalls', filter_edges=['has_syscall'], direction='out', max=1)[0]
        self._syscalls = self.get_connected_to(db, 'syscalls', filter_edges=['has_syscall'], max=1, 
                                               direction="out", limit=limit, skip=skip, sort_by=('syscalls', 'timestamp', "ASC"))

    def add_child_process(self, proc_path, pid, command_line):
        child_proc = Process.new(proc_path, pid, command_line)
        self._child_processes.append(child_proc)
        return child_proc

                
    def add_event(self, event_key, event_src=None, event_dest=None, event_data=None, event_time=None):
        new_event = Event()
        new_event.key = event_key
        if event_src:
            new_event.src = event_src
        if event_dest:
            new_event.dest = event_dest
        if event_data:
            new_event.data = event_data
        if event_time is None:
            new_event.time = self._event_counter
            self._event_counter += 1
        else:
            new_event.time = event_time

        self._events.append(new_event)
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

    @property
    def events(self):
        return self._events
    
    @property
    def syscalls(self):
        return self._syscalls
    
    @property
    def syscall_total(self):
        return self._syscall_total

    @property
    def event_count(self):
        if self._event_count == -1:
            return len(self._events)
        else:
            return self._event_count

    @property
    def uuid(self):
        return self._uuid

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
        self._src_port = data_obj.get('src_port', '')
        self._dest_addr = data_obj.get('dest_addr', '')
        self._dest_port = data_obj.get('dest_port', '')

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