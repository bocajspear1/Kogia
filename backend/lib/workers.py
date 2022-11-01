import threading
import queue
import time
import traceback

class FileWorker (threading.Thread):
    def __init__(self, plugin_list, job, file_obj):
        threading.Thread.__init__(self)
        
        self._file_obj = file_obj
        self._job = job
        self._plugin_list = plugin_list 
        self._subworkers = []
        self.daemon = True 

    def run(self):
        order = ('identify', 'unarchive', 'unpack', 'syscalls', 'metadata', 'signature')

        for i in range(len(order)):
            stage = order[i]
            for plugin in self._plugin_list:
                if plugin.PLUGIN_TYPE == stage and plugin.operates_on(self._file_obj):
                    try:
                        new_file_uuids = plugin.run(self._job, self._file_obj)
                    except Exception as e:
                        message = str(e) + ": " + str(traceback.format_exc())
                        self._job.error_log(plugin.__class__.__name__, message)
                        self._job.add_to_error(f"Plugin {plugin.__class__.__name__} had a failure")
                        print(message)

                    for new_file_uuid in new_file_uuids:
                        new_file_obj = self._job.submission.get_file(uuid=new_file_uuid)
                        new_file_obj.save(self._job.db)
                        new_file_worker = FileWorker(self._plugin_list, self._job, new_file_obj)
                        new_file_worker.start()
                        self._subworkers.append(new_file_worker)

        for worker in self._subworkers:
            worker.join()
                

class JobWorker(threading.Thread):
    def __init__(self, plugin_manager, job):
        threading.Thread.__init__(self)
        self._job = job
        self._pm = plugin_manager

    def run(self):
        
        
        workers = []
        file_list = self._job.submission.get_files()
        for i in range(len(file_list)):
            plugin_list = self._job.get_initialized_plugin_list(self._pm)
            
            new_file_worker = FileWorker(plugin_list, self._job, file_list[i])
            new_file_worker.start()
            workers.append(new_file_worker)

        for worker in workers:
            worker.join()

        self._job.complete = True
        self._job.save()
        print(f"Job {self._job.uuid} done")
                

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
            