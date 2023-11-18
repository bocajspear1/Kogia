import multiprocessing



def run_worker_receivers(config, workers):
    for worker in workers:
        worker.start_worker_receivers()

        
def run_gunicorn(config, workers, address, port):

    import gunicorn.app.base
    from gunicorn import util

    run_worker_receivers(config, workers)

    def number_of_workers():
        return 1
        # return (multiprocessing.cpu_count() * 2) + 1

    options = {
        'bind': '%s:%s' % (address, port),
        'workers': number_of_workers(),
        "access-logfile": "./logs/kogia-web.log",
        "certfile": "cert.pem",
        "keyfile": "key.pem",
        # "loglevel": "debug"
    }

    class StandaloneApplication(gunicorn.app.base.BaseApplication):

        def __init__(self, app_uri, options=None):
            self.app_uri = app_uri
            self.options = options
            super().__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items()
                    if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return util.import_app(self.app_uri)

    StandaloneApplication("backend.server:app", options).run()

def run_waitress(config, workers, address, port):
    from waitress import serve
    from backend.server import app

    run_worker_receivers(config)

    serve(app, listen='%s:%s' % (address, port))