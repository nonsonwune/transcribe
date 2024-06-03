import os
import psutil
import logging


def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    logging.info(f"Memory usage: {memory_info.rss / (1024 * 1024)} MB")
