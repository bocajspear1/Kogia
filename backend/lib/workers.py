import threading
import queue
import time
import traceback
import logging
import platform


from backend.lib.job import Job
from backend.version import VERSION
from backend.lib.db import ArangoConnection
from backend.lib.system import get_system_string, get_local_storage, get_memory_total, get_cpu_usage, get_memory_percent


class FileThreadSync:
    def __init__(self):
        self._run_queue = queue.Queue()
        self._save_lock = threading.RLock()

    @property
    def save_lock(self):
        return self._save_lock

    def get_runtoken(self, token):
        # Check if my token is 0
        if token == 0:
            # Wait until I can get a token
            token = self._run_queue.get()
        return token
    
    def pass_runtoken(self, token):
        # Put my token back into the queue and wait again
        self._run_queue.put(token)
        time.sleep(0.1)
        return 0

# This runs plugins on a single file
class FileThread (threading.Thread):
    def __init__(self, sync : FileThreadSync, my_token, new_queue, plugin_list, job, file_obj):
        threading.Thread.__init__(self)
        
        self._file_obj = file_obj
        self._job = job
        self._plugin_list = plugin_list 
        self.daemon = True 
        self._new_queue = new_queue
        self._sync = sync
        self._token = my_token
        self._logger = logging.getLogger(f"file-{file_obj.uuid}")


    def run(self):
        order = ('identify', 'unarchive', 'unpack', 'syscall', 'metadata', 'signature')

        self._job.info_log("JOB", f"Starting file thread for file {self._file_obj.uuid}")

        for i in range(len(order)):
            stage = order[i]

            self._token = self._sync.get_runtoken(self._token)
            
            self._logger.info("At stage %s for %s", stage, self._file_obj.name)

            # print(self._plugin_list)

            for plugin in self._plugin_list:
                # Is this file the primary file
                is_primary = self._job.primary == self._file_obj.uuid

                if plugin.PLUGIN_TYPE == 'syscall' and not is_primary:
                    self._logger.info("%s not primary file for job, skipping syscall", self._file_obj.name)
                    continue

                if plugin.PLUGIN_TYPE == stage and plugin.operates_on(self._file_obj, is_primary):
                    self._logger.info("Running plugin %s:%s", stage, plugin.name)
                    self._job.info_log(plugin.name, f"Running plugin {plugin.name}")

                    new_file_uuids = []
                    try:
                        new_file_uuids = plugin.run(self._job, self._file_obj)
                    except Exception as e:
                        message = str(e) + ": " + str(traceback.format_exc())
                        self._job.error_log(plugin.name, message)
                        self._job.add_to_error(f"Plugin {plugin.name} had a failure")
                        print(message)

                    for new_file_uuid in new_file_uuids:
                        self._new_queue.put(new_file_uuid)
                    
                    # Syscall stage is special since syscalls are special.
                    # Since we know syscalls can reach thousands, we load in windows from the database
                    # Because of this, only after syscalls we need to ensure data is synced to the database
                    if plugin.PLUGIN_TYPE == 'syscall':
                        # We should only have one thread ever calling syscall plugins (the primary file)
                        # This is here for stupidity protection for the future
                        with self._sync.save_lock:
                            self._job.save_exec_instances()
                    self._logger.info("Plugin %s finished", plugin.name)
                elif plugin.PLUGIN_TYPE == stage:
                    self._logger.info("Skipping plugin %s:%s", stage, plugin.name)

            self._token = self._sync.pass_runtoken(self._token)

            self._job.info_log("JOB", f"Finished stage {stage}") 

        self._job.info_log("JOB", f"Completed all stages")  


class WorkerMonitorThread(threading.Thread):
    """
    Thread for polling and pushing local usage information to database
    """


    def __init__(self, runner_name, count_queue, db : ArangoConnection, fs):
        threading.Thread.__init__(self)

        self.db = db
        self.runner_name = runner_name
        self._count_queue = count_queue
        self.fs = fs
        self.daemon = True
        self._logger = logging.getLogger("WorkerMonitorThread")


    def run(self):
        self._logger.debug("Started monitoring thread")

        SLEEP_TIME_SECONDS = 15
        HISTORY_MINUTES = 5
        first_start = True

        while True:
            runner_data = self.db.get_by_match("runners", "name", self.runner_name)
            runner_id = None
            if runner_data is None:
                runner_data = {}
            else:
                runner_id = runner_data['_id']

            job_count = runner_data.get('job_count', 0)
            while not self._count_queue.empty():
                self._count_queue.get()
                print("Increment job count")
                job_count += 1
            runner_data['job_count'] = job_count
            
            runner_data['name'] = self.runner_name
            runner_data['version'] = VERSION
            runner_data['system'] = get_system_string()
            filestore_total, filestore_used = self.fs.get_space()
            runner_data['filestore_total'] = filestore_total
            runner_data['filestore_used'] = filestore_used
            local_total, local_used = get_local_storage()
            runner_data['localstore_total'] = local_total
            runner_data['localstore_used'] = local_used
            runner_data['updated'] = int(time.time())

            max_items = int((HISTORY_MINUTES * 60) / SLEEP_TIME_SECONDS)

            memory_history = runner_data.get('memory_usage', [])
            if first_start:
                memory_history = []
            memory_history.insert(0, get_memory_percent())

            if len(memory_history) > max_items:
                memory_history = memory_history[:max_items]

            runner_data['memory_usage'] = memory_history

            # Get CPU history
            cpu_history = runner_data.get('cpu_usage', [])
            if first_start:
                cpu_history = []
            cpu_history.insert(0, get_cpu_usage())

            if len(cpu_history) > max_items:
                cpu_history = cpu_history[:max_items]

            runner_data['cpu_usage'] = cpu_history

            if first_start:
                first_start = False

            if runner_id is None:
                self.db.insert("runners", runner_data)
            else:
                self.db.update("runners", runner_id, runner_data)

            time.sleep(SLEEP_TIME_SECONDS)

class BaseWorker():

    def __init__(self, config, db_factory, filestore, plugin_manager):
        self._config = config
        self._db_factory = db_factory
        self._pm = plugin_manager 
        self._filestore = filestore
        self._count_queue = queue.Queue()
        self._monitor = None

    def start_monitoring_thread(self):
        self._monitor = WorkerMonitorThread(self.runner_name(), self._count_queue, self._db_factory.new(), self._filestore)
        self._monitor.start()

    def runner_name(self):
        return platform.node()
    
    def increment_job(self):
        self._count_queue.put(1)

    


def process_job(runner_name, config, new_job : Job, pm, db, filestore, logger):
    new_job.runner = runner_name
    logger.info("Starting to process job %s", new_job.uuid)
    file_threads = []
    run_queue = queue.Queue()
    new_file_queue = queue.Queue()

    # Ensure all data is synced to DB and all loaded
    logger.info("Syncing job %s's data to database", new_job.uuid)
    new_job.save()
    new_job.load(pm)
    
    # Set maximum number of FileThreads operating at a time
    max_file = config.get('max_file', 1)
    current_token = 1
    logger.info("Max file processing is %d", max_file)
    file_list = new_job.submission.files

    syncer = FileThreadSync()

    for i in range(len(file_list)):
        
        current_file = file_list[i]
        print(current_file.uuid, current_file.name, current_file.dropped, new_job.limited_to)
        
        # If the job is limited to certain files, ignore all others
        if len(new_job.limited_to) > 0 and not current_file.uuid in new_job.limited_to:
            continue
        plugin_list = new_job.get_initialized_plugin_list(pm)

        # Any token > 0 means you can run, 0 means you wait
        my_token = current_token
        if current_token > max_file:
            my_token = 0
        else:
            current_token += 1
        
        new_file_worker = FileThread(syncer, my_token, new_file_queue, plugin_list, new_job, current_file)
        new_file_worker.start()
        file_threads.append(new_file_worker)

    # Wait for the file threads to finish
    for worker in file_threads:
        worker.join()

    # Save job here
    logger.info("Saving job %s's data to database before new files", new_job.uuid)
    new_job.save()

    # Empty the new_file_queue and create a new job for them
    new_file_uuids = []
    while not new_file_queue.empty():
        new_file_uuids.append(new_file_queue.get())

    # Run identify job on new files
    if len(new_file_uuids) > 0:
        if new_job.primary is not None and new_job.primary != "": 
            logger.info("Creating sub-job")
            subjob = Job.new(new_job.submission, None, db, filestore)

            for new_file_uuid in new_file_uuids:
                subjob.add_limit_to_file(new_file_uuid)
            identify_plugins = pm.get_plugin_list('identify')
            subjob.add_plugin_list(identify_plugins)
            unarchive_plugins = pm.get_plugin_list('unarchive')
            subjob.add_plugin_list(unarchive_plugins)
            subjob.save()

            # Now lets run our identify job
            try:
                process_job(runner_name, config, subjob, pm, db, filestore, logger)
            except Exception as e:
                logger.error("Exception in sub-job: " + str(e))

            # Submission may have changed in subjob, ensure it is synced
            # Job's internal syncing ensures submission object is different
            new_job.submission.load(db)
            new_job.submission.load_files(db, filestore)
        else:
            logger.info("Adding new and re-running job")
            for new_file_uuid in new_file_uuids:
                new_job.add_limit_to_file(new_file_uuid)

            # Now lets rerun our identify job
            process_job(runner_name, config, new_job, pm, db, filestore, logger)
            # Don't save again since our re-run should save for us
            return
    # else:
    new_job.complete = True
    logger.info("Saving job %s data...", new_job.uuid)
    new_job.info_log("JOB", "Job completed")
    new_job.save()
    logger.info("Job %s done", new_job.uuid)

class WorkerManager():
    
    def __init__(self):
        self._workers = []
        self._next = 0
        self._logger = logging.getLogger("WorkerManager")

    @property
    def worker_count(self):
        return len(self._workers)

    def add_worker(self, new_worker):
        self._workers.append(new_worker)

    def assign_job(self, job_id):
        if len(self._workers) > 0:
            self._logger.info("Assigned job to %s", self._workers[self._next].__class__.__name__)
            self._workers[self._next].assign_job(job_id)
            self._next += 1
            if self._next >= len(self._workers):
                self._next = 0
        else:
            raise ValueError("No workers were added!")


# class JobWorkerManager(threading.Thread):
#     def __init__(self, in_queue, db):
#         threading.Thread.__init__(self)

# class PluginListWorkerManager (threading.Thread):
#     def __init__(self, plugin_list, in_queue, db, next_queue=None):
#         threading.Thread.__init__(self)
#         self._in_queue = in_queue 
#         self._complete_queue = queue.Queue()
#         self._plugin_list = plugin_list 
#         self._db = db
#         self.daemon = True 
#         self._next_queue = next_queue
#         self._threads = []

#     def run(self):
#         while True:
#             try:
#                 input_tuple = self._new_queue.get()
#                 submission = input_tuple[0]
#                 file_obj = input_tuple[1]

#                 new_worker = PluginListWorker(self._plugin_list, self._complete_queue, submission, file_obj)
#                 new_worker.start()
#                 self._threads.append(new_worker)
#             except queue.Empty:
#                 pass
#             try:
#                 input_tuple = self._complete_queue.get()
#                 submission = input_tuple[0]
#                 file_obj = input_tuple[1]
#                 submission.save(self._db)
#                 file_obj.save(self._db)
#                 if self._next_queue is not None:
#                     self._next_queue
#             except queue.Empty:
#                 pass

#             done_list = []
#             for i in range(len(self._threads)):
#                 if not self._threads[i].is_alive():
#                     done_list.append(self._threads[i])
            
#             for item in done_list:
#                 self._threads.remove(item)

#             time.sleep(0.1)
            