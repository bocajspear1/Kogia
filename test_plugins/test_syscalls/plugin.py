from backend.lib.plugin_base import PluginBase
import shutil
from io import BytesIO

from PIL import Image

from datetime import datetime, timedelta

from backend.lib.job import Job

class TestSyscallPlugin(PluginBase):
    """
    Test plugin that fakes a syscall-type plugin.
    """
    PLUGIN_TYPE = 'syscall'
    INGESTS = []

    def __init__(self, plugin_manager, args=None):
        super().__init__(plugin_manager)
        self.args = args
        print(args)

    def run(self, job : Job, file_obj):

        new_exec = job.add_exec_instance('test_syscall', "fake os")
        new_exec.start_time = (datetime.now()-timedelta(minutes=5)).timestamp()
        new_exec.end_time = datetime.now().timestamp()

        if self.args['raise_exception']:
            raise ValueError("Something went wrong, but not really")
        
        if self.args['add_screenshots']:

            color = [0, 0, 0]

            for i in range(3):
                screenshot_color = color
                screenshot_color[i] = 155
                file = BytesIO()
                image = Image.new('RGBA', size=(1920, 1080), color=tuple(screenshot_color))
                image.save(file, 'png')
                file.name = f'test-{i}.png'
                file.seek(0)

                job.add_screenshot(new_exec, file)

        if self.args['add_processes']:
            job.info_log(self.name, "Adding processes")

            new_proc = new_exec.add_process("/test/test.fake", 16, "test.fake arg1 arg2")

            child_proc = new_proc.add_child_process("/test/child.fake", 22, "child.fake arg1 arg2")

            event_counter = 0

            event_keys = [
                "FILE_OPEN",
                "FILE_READ",
                "FILE_CLOSE",
                "SOCKET_OPEN",
                "SOCKET_CONNECT",
                "SOCKET_CLOSE"
            ]

            if self.args['add_events']:
                job.info_log(self.name, "Adding events")

                for i in range(3):
                    new_proc.add_event(event_keys[event_counter], "SRC", "DEST", "DATA GOES HERE", event_counter, True)
                    event_counter += 1

                for i in range(3):
                    child_proc.add_event(event_keys[event_counter], "SRC", "DEST", "DATA GOES HERE", 2, True)
                    event_counter += 1

            if self.args['add_networking']:
                job.info_log(self.name, "Adding networking")
                new_exec.add_network_comm("fake", "1.1.1.1", 80, "1.1.1.2", 9090, "data is here", 1)
                new_exec.add_network_comm("fake", "1.1.1.2", 9090, "1.1.1.1", 80, "data is here", 2)

            if self.args['add_libraries']:
                job.info_log(self.name, "Adding libraries")
                new_proc.add_shared_lib("/lib/fake.lib")
                new_proc.add_shared_lib("/lib/secure.lib")

                child_proc.add_shared_lib("/lib/secure.lib")

            if self.args['add_metadata']:
                job.info_log(self.name, "Adding metadata")
                new_exec.add_metadata("EXEC_METADATA1", "COOL")

                new_proc.add_metadata("METADATA1", "VALUE1")
                for i in range(3):
                    new_proc.add_metadata("INCREMENT", f"VALUE_INC_{i}")

                child_proc.add_metadata("METADATA1", "VALUE1")
                for i in range(3):
                    child_proc.add_metadata("INCREMENT", f"VALUE_INC_{i}")

            if self.args['add_syscalls']:
                job.info_log(self.name, "Adding syscalls")

                new_proc.add_syscall("open", ['a', 'b'], 1, 1, 42)
                new_proc.add_syscall("read", ['1'], 0, 2, 42)
                new_proc.add_syscall("close", ['1'], 0, 2, 42)

                child_proc.add_syscall("open", ['a', 'b'], 2, 1, 42)
                child_proc.add_syscall("connect", ['2', '192.168.1.1', '9090'], 0, 2, 42)
                child_proc.add_syscall("close", ['2'], 0, 2, 42)

        if self.args['add_report']:
            job.info_log(self.name, "Adding report")
            job.add_report("Test Report", file_obj, "This is a report!")

        if self.args['add_dropped_files']:
            job.info_log(self.name, "Adding dropped file")
            dropped = job.submission.generate_file("dropped1.txt")
            dropped.create_file()
            dropped.write_to_file(b"This is a some data in the dropped file!")
            job.submission.add_file(dropped, dropped=True)

        if self.args['log_error']:
            job.error_log(self.name, "This is an error")

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