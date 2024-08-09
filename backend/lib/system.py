import platform

import psutil

def get_local_storage():
    main_disk = psutil.disk_usage('/')
    return main_disk.total, main_disk.used

def get_system_string():
    return "{} - {} {}".format(platform.node(), platform.system(), platform.release())

def get_memory_usage():
    memory = psutil.virtual_memory() 
    return memory.total, memory.used

def get_memory_total():
    total, _ = get_memory_usage()
    return total

def get_memory_percent():
    total, used = get_memory_usage()
    return round((used / total) * 100, 2)

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)