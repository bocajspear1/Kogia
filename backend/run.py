import multiprocessing
import logging
import time
from backend.lib.helpers import configure_logging

logger = logging.getLogger(__name__)

def run_worker_receivers(config, workers):
    for worker in workers:
        worker.start_worker_receivers()
        worker.start_monitoring_thread()

def run_workers_only(config, workers):

    configure_logging(config, extra="workers")

    logger.info("Starting workers")
    run_worker_receivers(config, workers)
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        for worker in workers:
            worker.stop_worker_receivers()

def run_uvicorn(config, workers, address, port, insecure):

    configure_logging(config)

    run_worker_receivers(config, workers)

    def number_of_workers():
        return 1
        # return (multiprocessing.cpu_count() * 2) + 1


    import uvicorn

    app_name = "backend.main:app"
    access_log_path = "./logs/kogia-web.log"
    if 'access_log_path' in config:
        access_log_path = config['access_log_path']

    server_config = None
    if not insecure:
        server_config = uvicorn.Config(app_name, 
                                host=address, 
                                port=port, 
                                access_log=access_log_path,
                                workers=number_of_workers(),
                                ssl_keyfile=config['keyfile'],
                                ssl_certfile=config['certfile']
                            )
    else:
        server_config = uvicorn.Config(app_name, 
                                host=address, 
                                port=port, 
                                access_log=access_log_path,
                                workers=number_of_workers()
                            )
    server = uvicorn.Server(server_config)
    server.run()
