from backend.lib.plugin_base import HTTPPluginBase
import shutil
import os
import time

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

    def _process_thread(self, process, thread_id, thread_syscalls):
        for item in thread_syscalls:

            process.add_syscall(
                item['api'], 
                item['args'], 
                item['ret'], 
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

    def _add_child_process(self, process_list, exec_instance=None, parent_proc=None):
        for process in process_list:
            print(process['path'], process['pid'])

            if exec_instance is not None:
                new_proc = exec_instance.add_process(process['path'], process['pid'])
            elif parent_proc is not None:
                new_proc = parent_proc.add_child_process(process['path'], process['pid']) 

            for lib_path in process['libraries']:
                new_proc.add_metadata("LOADED_LIBRARY", lib_path.lower()) 
                new_proc.add_shared_lib(lib_path)

            for thread in process['threads']:
                self._process_thread(new_proc, thread, process['threads'][thread])

            if 'child_processes' in process:
                self._add_child_process(process['child_processes'], parent_proc=new_proc)

    def run(self, job, file_obj):
        
        minke_uuid = self.args.get("uuid", '')

        print(minke_uuid)

        if minke_uuid.strip() == '':

            file_data = None

            if len(job.submission.files) == 1:
                file_data = {
                    'sample': file_obj.file
                }
            else:
                file_data = [
                    ('samples', (file_obj.name, file_obj.file, 'application/octet-stream'))
                ]

                for extra_file in job.submission.files:
                    if extra_file.hash != file_obj.hash:
                        file_data.append(('samples', (extra_file.name, extra_file.file, 'application/octet-stream')))
            
            print('file_data', file_data)
            resp = self.post("/api/v1/samples/submit", files=file_data, data={
                'exec': file_obj.name
            })

            print(resp.json())
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

                self._add_child_process(process_data, exec_instance=new_exec)




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
        
        return [{"Minke Version": version}]
    
    def action_get_job_count(self):
        job_count = "UNKNOWN"
        resp = self.get("/api/v1/jobs/count")
        resp_json = resp.json()
        if resp_json['ok'] == True:
            job_count = resp_json['result']['count']
        
        return [{"Job Count": job_count}]

__PLUGIN__ = MinkePlugin