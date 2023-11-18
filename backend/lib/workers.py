import threading
import queue
import time
import traceback

from backend.lib.job import Job




class WorkerManager():
    
    def __init__(self):
        self._workers = []
        self._next = 0

    @property
    def worker_count(self):
        return len(self._workers)

    def add_worker(self, new_worker):
        self._workers.append(new_worker)

    def assign_job(self, job_id):
        if len(self._workers) > 0:
            print("Assigned job to {}".format(self._workers[self._next].__class__.__name__))
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
            