from backend.lib.plugin_base import HTTPPluginBase
import base64
import ast
import time
from datetime import datetime
import shlex

class MinkePlugin(HTTPPluginBase):
    PLUGIN_TYPE = 'syscall'
    INGESTS = []

    def __init__(self, plugin_manager, args=None):
        super().__init__(plugin_manager)
        self.configure(
            self.config['host'],
            self.config['ssl'],
            self.config['ssl_verify'],
            {"x-api-key": self.config['apikey']},
        )
        if args is not None:
            self.args = args
        else:
            self.args = {}

        self._fd_map = {}
        self._qemu_root = None
        self._time_start = None

    def _process_thread(self, process, thread_id, thread_syscalls, operating_system):
        for item in thread_syscalls:

            if operating_system == "windows":

                process.add_syscall(
                    item['api'], 
                    item['args'], 
                    item['return'], 
                    item['counter'],
                    int(thread_id)
                )

                if item['api'] in ("kernel32.createfilew", "kernel32.createfilea"):
                    path = item['args'][0][1:-1]
                    process.add_event("CREATE_FILE", event_src=path)
                elif item['api'] in ("kernel32.createprocessw", "kernel32.createprocessa"):
                    exec_path = item['args'][0][1:-1]
                    if item['args'][1].startswith("\""):
                        exec_path = item['args'][1][1:-1]

                    event_data = "FAILED"
                    if item['ret'] > 0:
                        event_data = "SUCCESS"

                    process.add_event("CREATE_PROCESS", event_src=exec_path, event_data=event_data)
                elif item['api'] in ("advapi32.regopenkeyexw", "advapi32.regopenkeyexa"):
                    top_level_num = item['args'][0]
                    top_level = "???"
                    if top_level_num == "ffffffff80000001":
                        top_level = "HKEY_CURRENT_USER"
                    elif top_level_num == "ffffffff80000002":
                        top_level = "HKEY_LOCAL_MACHINE"
                    elif top_level_num == "ffffffff80000003":
                        top_level = "HKEY_USERS"
                    elif top_level_num == "ffffffff80000005":
                        top_level = "HKEY_CURRENT_CONFIG"
                    elif top_level_num == "ffffffff80000006":
                        top_level = "HKEY_DYN_DATA"


                    reg_path = item['args'][1][1:-1]

                    full_path = top_level + "\\" + reg_path

                    event_data = "FAILED"
                    if item['ret'] == 0:
                        event_data = "SUCCESS"

                    process.add_event("OPEN_REGISTRY_KEY", event_src=full_path, event_data=event_data)

            elif operating_system == "linux": 
                syscall = item['syscall']

                if process.pid not in self._fd_map:
                    self._fd_map[process.pid] = {}

                my_time = datetime.strptime(item['time'], "%H:%M:%S.%f")
                time_offset = 0
                if self._time_start is None:
                    self._time_start = my_time
                else:
                    time_offset = (my_time - self._time_start).microseconds

                if syscall.startswith("process:"):
                    process.add_event(f"EXIT", event_src=f"{process.pid}:{thread_id}")

                else:
                    process.add_syscall(
                        syscall, 
                        item['args'], 
                        item['return'], 
                        time_offset,
                        int(thread_id)
                    )

                    if syscall in ("open", "creat"):
                        path = item['args'][0][1:-1]

                        if self._qemu_root is not None and self._qemu_root in path:
                            path = path.replace(self._qemu_root, "")

                        action = None
                        if syscall == "creat" or "O_CREAT" in item['args'][1][1:-1]:
                            action = "CREATE"
                        else:
                            action = "OPEN"

                        success = True
                        event_data = None
                        if item['return'].startswith("-1"):
                            success = False
                            event_data = item['return'][3:]
                        else:
                            self._fd_map[process.pid][item['return']] = path
                        process.add_event(f"{action}_FILE", event_src=path, event_success=success, event_data=event_data)

                        
                    elif syscall in ('execve', 'execveat', 'fexecve'):
                        command_line = None
                        env_vals = None
                        if syscall in ('execve', 'fexecve'):
                            env_vals = item['args'][2]
                            command_line = shlex.join(item['args'][1])
                        else:
                            env_vals = item['args'][3]
                            command_line = shlex.join(item['args'][2])


                        for env_val in env_vals:
                            env_val = env_val[1:-1]
                            if env_val.startswith("PWD="):
                                pwd_split = env_val.split("=")
                                self._fd_map[process.pid]['AT_FDCWD'] = pwd_split[1]
                        
                        # Set the path that QEMu considers "root", use this to remove from paths accessed.
                        if command_line.startswith("qemu-") and "-L " in command_line:
                            self._qemu_root = command_line.split("-L ")[1].split(" ")[0]

                        process.add_event("CREATE_PROCESS", event_src=command_line)
                    elif syscall in ('chdir', 'fchdir'):
                        new_cwd = None
                        if syscall == 'chdir':
                            new_cwd = item['args'][0][1:-1]
                        else:
                            new_cwd =  self._fd_map[process.pid][item['args'][0]]
                        self._fd_map[process.pid]['AT_FDCWD'] = new_cwd

                    elif syscall in ('openat', 'openat2'):
                        path = item['args'][1][1:-1]
                        if not path.startswith("/"):
                            path = self._fd_map[process.pid][item['args'][0]] + "/" + path

                        if self._qemu_root is not None and self._qemu_root in path:
                            path = path.replace(self._qemu_root, "")

                        action = None
                        if "O_CREAT" in item['args'][2][1:-1]:
                            action = "CREATE"
                        else:
                            action = "OPEN"

                        success = True
                        event_data = None
                        if item['return'].startswith("-1"):
                            success = False
                            event_data = item['return'][3:]
                        else:
                            self._fd_map[process.pid][item['return']] = path
                        process.add_event(f"{action}_FILE", event_src=path, event_success=success, event_data=event_data)

                    elif syscall == "read":
                        path = self._fd_map[process.pid][item['args'][0]]
                        process.add_event(f"READ_FILE", event_src=path, event_data=item['args'][2])
                    elif syscall == "pipe2":
                        
                        self._fd_map[process.pid][item['args'][0][1]] = "PIPE"
                        self._fd_map[process.pid][item['args'][0][0]] = "PIPE"

                    elif syscall == "dup":
                        fd = item['args'][0]
                        if fd in self._fd_map[process.pid]:
                            self._fd_map[process.pid][item['return']] =  self._fd_map[process.pid][fd]
                    elif syscall in ("dup2", "dup3"):
                        old_fd = item['args'][0]
                        new_fd = item['args'][1]
                        if old_fd in self._fd_map[process.pid]:
                            self._fd_map[process.pid][new_fd] =  self._fd_map[process.pid][old_fd]

                    elif syscall == "close":
                        fd = item['args'][0]
                        if fd != "-1" and fd in self._fd_map[process.pid]:
                            path = self._fd_map[process.pid][fd]
                            process.add_event(f"CLOSE", event_src=path)
                            del self._fd_map[process.pid][fd]
                        else:
                            print(f"Found fd {fd} not in process")
                    elif syscall == "socket":
                        process.add_event(f"CREATE_SOCKET")

                        self._fd_map[process.pid][item['return']] = "SOCKET"
                    elif syscall == "connect":
                        conn_data = item['args'][1]
                        dest_addr = "unknown"
                        dest_port = "??"

                        if conn_data['sin_port'].startswith("htons("):
                            dest_port = conn_data['sin_port'][6:-1]
                        if conn_data['sin_addr'].startswith("inet_addr("):
                            dest_addr = ast.literal_eval(f"b\"{conn_data['sin_addr'][11:-2]}\"").decode()


                        process.add_event(f"CONNECT", event_dest=f"{dest_addr}:{dest_port}")


    def _add_child_process(self, process_list, operating_system, exec_instance=None, parent_proc=None):
        for process in process_list:

            if exec_instance is not None:
                new_proc = exec_instance.add_process(process['path'], process['pid'], process['command_line'])
            elif parent_proc is not None:
                new_proc = parent_proc.add_child_process(process['path'], process['pid'], process['command_line']) 

            for lib_path in process['libraries']:
                new_proc.add_metadata("LOADED_LIBRARY", lib_path.lower()) 
                new_proc.add_shared_lib(lib_path)

            for thread in process['threads']:
                self._process_thread(new_proc, thread, process['threads'][thread], operating_system)

            if 'child_processes' in process:
                self._add_child_process(process['child_processes'], operating_system, parent_proc=new_proc)

    def run(self, job, file_obj):
        
        minke_uuid = self.args.get("uuid", '')

        if minke_uuid.strip() == '':

            file_data = None

            if len(job.submission.files) == 1:
                file_data = {
                    'sample': file_obj.open_file()
                }
            else:
                file_data = [
                    ('samples', (file_obj.name, file_obj.open_file(), 'application/octet-stream'))
                ]

                for extra_file in job.submission.files:
                    if extra_file.hash != file_obj.hash:
                        file_data.append(('samples', (extra_file.name, extra_file.open_file(), 'application/octet-stream')))
            
            
            resp = self.post("/api/v1/samples/submit", files=file_data, data={
                'exec': file_obj.name
            })

            
            resp_json = resp.json()
            if resp_json['ok'] == True:
                minke_uuid = resp_json['result']['job_id']

        done = False
        waited_time = 0
        max_time = (int(self.args.get('exectime', 3)) * 60) * 2

        while not done and waited_time < max_time:
            resp_json = self.get(f"/api/v1/jobs/{minke_uuid}/info").json()
            if resp_json['ok'] == True: 
                if resp_json['result']['info']['complete'] is True:
                    done = True
                else:
                    time.sleep(5)
                    waited_time += 5
        
        if done:
            job.info_log(str(self.__class__.__name__), f"Job {minke_uuid} is done")
            info_json = self.get(f"/api/v1/jobs/{minke_uuid}/info").json()

            resp_json = self.get(f"/api/v1/jobs/{minke_uuid}/syscalls").json() 
            if resp_json['ok'] == True: 
                process_data = resp_json['result']['processes']
                new_exec = job.add_exec_instance('minke', resp_json['result']['operating_system'])
                new_exec.start_time = info_json['result']['info']['start_time']
                new_exec.end_time = info_json['result']['info']['end_time']

                self._add_child_process(process_data, resp_json['result']['operating_system'], exec_instance=new_exec)

                resp_json = self.get(f"/api/v1/jobs/{minke_uuid}/info").json() 
                if resp_json['ok'] != True: 
                    job.error_log(self.name, "Unable to get execution into")
                    return []
                exec_info = resp_json['result']['info']
                
                resp_json = self.get(f"/api/v1/jobs/{minke_uuid}/networking").json() 
                if resp_json['ok'] == True: 
                    results = resp_json['result']
                    for net_data_key in results['net_data']:
                        net_data_split = net_data_key.split("|")
                        for connection in results['net_data'][net_data_key]:
                            if connection[0] != "":
                                new_exec.add_network_comm(net_data_split[0], exec_info['ip_addr'], 5555, net_data_split[1], int(net_data_split[2]), base64.b64decode(connection[0]).decode())
                            if connection[1] != "":
                                new_exec.add_network_comm(net_data_split[0], net_data_split[1], int(net_data_split[2]), exec_info['ip_addr'], 5555, base64.b64decode(connection[1]).decode())

                if len(exec_info['written_files']) > 0:
                    for dropped_name in exec_info['written_files']:
                        dropped = job.submission.generate_file(dropped_name)
                        dropped.create_file()

                        dropped_resp = self.get(f"/api/v1/jobs/{minke_uuid}/dropped/{dropped_name}")
                        if dropped_resp.status_code != 404:
                            dropped.write_to_file(dropped_resp.content)
                            job.submission.add_file(dropped, dropped=True)
                            job.info_log(self.name, f"Adding dropped file {dropped_name}")
                        else:
                            job.error_log(self.name, f"Unable to get file {dropped_name}")




        return []

    def check(self):
        resp = self.get("/api/v1/version")
        resp_json = resp.json()
        if not resp_json['ok'] == True:
            raise ValueError("Cannot connect to Minke instance")
        
    def action_get_version(self):
        version = "UNKNOWN"
        resp = self.get("/api/v1/version")
        resp_json = resp.json()
        if resp_json['ok'] == True:
            version = resp_json['result']['version']
        
        return {"Minke Version": version}
    
    def action_get_job_count(self):
        job_count = "UNKNOWN"
        resp = self.get("/api/v1/jobs/count")
        resp_json = resp.json()
        if resp_json['ok'] == True:
            job_count = resp_json['result']['count']
        
        return {"Job Count": job_count}

__PLUGIN__ = MinkePlugin