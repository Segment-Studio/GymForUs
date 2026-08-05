import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = max(2, multiprocessing.cpu_count() // 2)
threads = 2
worker_class = "gthread"
keepalive = 5
timeout = 30
max_requests = 1000
max_requests_jitter = 100
preload_app = False
accesslog = "-"
errorlog = "-"
loglevel = "info"
