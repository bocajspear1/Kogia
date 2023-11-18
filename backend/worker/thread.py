import threading
import multiprocessing
import queue
import traceback

from backend.lib.job import Job

def number_of_workers():
    return 2
    # return (multiprocessing.cpu_count() * 2) + 1


# This runs plugins on a single file
class FileThread (threading.Thread):
    def __init__(self, new_queue, plugin_list, job, file_obj):
        threading.Thread.__init__(self)
        
        self._file_obj = file_obj
        self._job = job
        self._plugin_list = plugin_list 
        self.daemon = True 
        self._new_queue = new_queue

    def run(self):
        order = ('identify', 'unarchive', 'unpack', 'syscall', 'metadata', 'signature')

        for i in range(len(order)):
            stage = order[i]
            print("* {} - STAGE: {}".format(self._file_obj.name, stage))
            for plugin in self._plugin_list:
                if plugin.PLUGIN_TYPE == 'syscall' and self._job.primary != self._file_obj.uuid:
                    print("{} not primary file for job, skipping syscall".format(self._file_obj.name))
                    continue
                if plugin.PLUGIN_TYPE == stage and plugin.operates_on(self._file_obj):
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
                

class ThreadWorkerInst(threading.Thread):
    def __init__(self, id, queue, db, filestore, plugin_manager):
        threading.Thread.__init__(self)
        self._id = id
        self.db = db
        self.filestore = filestore
        self.queue = queue
        self.pm = plugin_manager
        self.daemon = True

    def _process_job(self, new_job):
        
        file_threads = []
        new_file_queue = queue.Queue()
        file_list = new_job.submission.files
        for i in range(len(file_list)):
            current_file = file_list[i]
            print(current_file.uuid, current_file.name, new_job.limited_to)
            # print(new_job.limited_to)
            # If the job is limited to certain files, ignore all others
            if len(new_job.limited_to) > 0 and not current_file.uuid in new_job.limited_to:
                continue
            plugin_list = new_job.get_initialized_plugin_list(self.pm)
            
            new_file_worker = FileThread(new_file_queue, plugin_list, new_job, current_file)
            new_file_worker.start()
            file_threads.append(new_file_worker)

        # Wait for the file threads to finish
        for worker in file_threads:
            worker.join()

        # Save job here
        new_job.save()

        # Empty the new_file_queue and create a new job for them
        new_file_uuids = []
        while not new_file_queue.empty():
            new_file_uuids.append(new_file_queue.get())

        # Run identify job on new files
        if len(new_file_uuids) > 0:
            if new_job.primary is not None and new_job.primary != "": 
                print("Creating sub-job")
                subjob = Job.new(new_job.submission, None, self.db, self.filestore)

                for new_file_uuid in new_file_uuids:
                    subjob.add_limit_to_file(new_file_uuid)
                    identify_plugins = self.pm.get_plugin_list('identify')
                    subjob.add_plugin_list(identify_plugins)
                    unarchive_plugins = self.pm.get_plugin_list('unarchive')
                    subjob.add_plugin_list(unarchive_plugins)
                    subjob.save()

                    # Now lets run our identify job
                    self._process_job(subjob)
                    # new_job.save()
            else:
                print("Adding new and re-running job")
                for new_file_uuid in new_file_uuids:
                    new_job.add_limit_to_file(new_file_uuid)

                # Now lets rerun our identify job
                self._process_job(new_job)
                # Don't save again since our re-run should save for us
        else:
            new_job.complete = True
            print(f"Saving Job {new_job.uuid} data...")
            new_job.save()
            print(f"Job {new_job.uuid} done")

    def run(self):
        print("Starting {} instance {}".format(self.__class__.__name__, self._id))
        while True:
            # Get a job from the queue
            job_id = self.queue.get()
            # Load the job's data
            new_job = Job(self.db, self.filestore, uuid=job_id)
            new_job.load(self.pm)

            self._process_job(new_job)
           

class WorkerThread():

    def __init__(self, config, db_factory, filestore, plugin_manager):
        self._config = config
        self._db_factory = db_factory
        self._pm = plugin_manager 
        self._filestore = filestore
        self._queue = queue.Queue()
        self._threads = []
    
    def start_worker_senders(self):
        thread_count = number_of_workers()
        for i in range(thread_count):
            new_thread = ThreadWorkerInst(i, self._queue, self._db_factory.new(), self._filestore, self._pm)
            self._threads.append(new_thread)
            new_thread.start()
        
        # for t in self._threads:
        #     t.join()

    def start_worker_receivers(self):
        pass

    def assign_job(self, job_id):
        self._queue.put_nowait(job_id)