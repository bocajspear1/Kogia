import threading
import queue
import time

class PluginListWorker (threading.Thread):
    def __init__(self, plugin_list, out_queue, submission, file_obj):
        threading.Thread.__init__(self)
        self._submission = submission
        self._file_obj = file_obj
        self._out_queue = out_queue
        self._plugin_list = plugin_list 
        self.daemon = True 

    def run(self):
        for plugin in self._plugin_list:
            if plugin.operates_on(self._file_obj):
                plugin.run(self._submission, self._file_obj)
        
        self._out_queue.put((self._submission, self._file_obj))

class PluginListWorkerManager (threading.Thread):
    def __init__(self, plugin_list, in_queue, db, next_queue=None):
        threading.Thread.__init__(self)
        self._in_queue = in_queue 
        self._complete_queue = queue.Queue()
        self._plugin_list = plugin_list 
        self._db = db
        self.daemon = True 
        self._next_queue = next_queue
        self._threads = []

    def run(self):
        while True:
            try:
                input_tuple = self._new_queue.get()
                submission = input_tuple[0]
                file_obj = input_tuple[1]

                new_worker = PluginListWorker(self._plugin_list, self._complete_queue, submission, file_obj)
                new_worker.start()
                self._threads.append(new_worker)
            except queue.Empty:
                pass
            try:
                input_tuple = self._complete_queue.get()
                submission = input_tuple[0]
                file_obj = input_tuple[1]
                submission.save(self._db)
                file_obj.save(self._db)
                if self._next_queue is not None:
                    self._next_queue
            except queue.Empty:
                pass

            done_list = []
            for i in range(len(self._threads)):
                if not self._threads[i].is_alive():
                    done_list.append(self._threads[i])
            
            for item in done_list:
                self._threads.remove(item)

            time.sleep(0.1)
            