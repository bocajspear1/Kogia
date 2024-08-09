import threading
import multiprocessing
import queue
import traceback
import logging

from backend.lib.job import Job
from backend.lib.workers import process_job, BaseWorker

logger = logging.getLogger(__name__)

def number_of_workers():
    return 2
    # return (multiprocessing.cpu_count() * 2) + 1


class ThreadWorkerInst(threading.Thread):
    def __init__(self, runner_name, id, config, queue, db, filestore, plugin_manager):
        threading.Thread.__init__(self)
        self._id = id
        self._runner_name = runner_name
        self.db = db
        self.filestore = filestore
        self.queue = queue
        self.pm = plugin_manager
        self.daemon = True
        self._config = config

    def run(self):
        logger.debug("Starting %s instance %d", self.__class__.__name__, self._id)
        while True:
            # Get a job from the queue
            job_id = self.queue.get()
            # Load the job's data
            new_job = Job(self.db, self.filestore, uuid=job_id)
            new_job.load(self.pm)

            process_job(self._runner_name, self._config, new_job, self.pm, self.db, self.filestore, logger)
           

class WorkerThread(BaseWorker):

    def __init__(self, config, db_factory, filestore, plugin_manager):
        super().__init__(config, db_factory, filestore, plugin_manager)

        self._queue = queue.Queue()
        self._threads = []
    
    def start_worker_senders(self):
        thread_count = number_of_workers()
        for i in range(thread_count):
            new_thread = ThreadWorkerInst(self.runner_name(), i, self._config, self._queue, self._db_factory.new(), self._filestore, self._pm)
            self._threads.append(new_thread)
            new_thread.start()
        
        # for t in self._threads:
        #     t.join()

    def start_worker_receivers(self):
        pass

    def assign_job(self, job_id):
        self.increment_job()
        self._queue.put_nowait(job_id)