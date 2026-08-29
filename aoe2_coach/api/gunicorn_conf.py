"""
Gunicorn + Uvicorn Production Worker Configuration for AoE2 Coach Gateway.
Optimized for high-concurrency RTS tactical decision-support traffic.
"""

import os
import multiprocessing

# Server socket
bind = os.getenv("BIND", "0.0.0.0:8000")
backlog = int(os.getenv("BACKLOG", "2048"))

# Worker processes
# For CPU-bound ML & sub-millisecond I/O, 2-4 workers per core is optimal
workers_default = max(2, min(8, (multiprocessing.cpu_count() * 2) + 1))
workers = int(os.getenv("WORKERS", str(workers_default)))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = int(os.getenv("WORKER_CONNECTIONS", "1000"))

# Lifecycle and timeouts
timeout = int(os.getenv("TIMEOUT", "30"))
keepalive = int(os.getenv("KEEP_ALIVE", "5"))
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "15"))
max_requests = int(os.getenv("MAX_REQUESTS", "5000"))
max_requests_jitter = int(os.getenv("MAX_REQUESTS_JITTER", "500"))

# Logging
loglevel = os.getenv("LOG_LEVEL", "info")
accesslog = os.getenv("ACCESS_LOG", "-")
errorlog = os.getenv("ERROR_LOG", "-")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sµs'

# Security & Process naming
proc_name = "aoe2-coach-api"
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
