from backend.lib.plugin_base import PluginBase
import shutil
import os
import time

from datetime import datetime, timedelta

from backend.lib.job import Job

class TestSyscallPlugin(PluginBase):
    PLUGIN_TYPE = 'syscall'
    INGESTS = []

    def __init__(self, plugin_manager, args=None):
        super().__init__(plugin_manager)
        self.args = args
        print(args)

    def run(self, job : Job, file_obj):
        
        minke_uuid = self.args.get("uuid", '')

        print(minke_uuid)

        new_exec = job.add_exec_instance('test_syscall', "fake os")
        new_exec.start_time = (datetime.now()-timedelta(minutes=5)).timestamp()
        new_exec.end_time = datetime.now().timestamp()

        new_proc = new_exec.add_process("/test/test.fake", 16, "test.fake arg1 arg2")

        new_proc.add_event("FILE_READ", "SRC", "DEST", "DATA GOES HERE", 1, True)

        child_proc = new_proc.add_child_process("/test/child.fake", 22, "child.fake arg1 arg2")

        child_proc.add_event("FILE_READ", "SRC", "DEST", "DATA GOES HERE", 2, True)

        return []

    def check(self):
        return True
        
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

__PLUGIN__ = TestSyscallPlugin