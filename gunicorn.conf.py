import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True

accesslog = "logs/access.log"
errorlog = "logs/gunicorn-error.log"
loglevel = os.getenv("LOG_LEVEL", "info").lower()
